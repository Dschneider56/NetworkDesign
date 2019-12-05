from socket import *
from time import sleep
import random as rnd
import logging
import hashlib
import math
import time
from threading import Thread
import datetime as dt

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

"""
To enable debugging statements, change the below level value to logging.DEBUG
To disable them, change level to logging.CRITICAL
"""
logging.basicConfig(level=logging.CRITICAL)  # For print statements, change CRITICAL to DEBUG. To disable them,
                                            # change DEBUG to CRITICAL.

SEQNUM_SIZE = 16  # Size of sequence number in bytes.
CHECKSUM_SIZE = 16  # Size of checksum in bytes.
PACKET_SIZE = 2048  # Size of a packet in bytes.
INITIALIZE = b'\r\n'  # The terminator character sequence.
TERMINATE = b'\n\r'  # The terminator character sequence.


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a certain size containing the data, a checksum,
    and a sequence number.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets = []            # all the packets
    packet_num = 0          # the packet number being evaluated, will double as the sequence number
    while len(data) > 0:    # Keep appending the packets to the packet list.
        try:
            if packet_num == 0:     # The very first packet should contain the total number of packets
                raw_packet = bytes(str(math.ceil((len(data) / PACKET_SIZE) + 1)), 'utf-8')
            else:
                raw_packet = data[:PACKET_SIZE]     # Extract the first "PACKET_SIZE" bytes into packet.
                data = data[PACKET_SIZE:]           # Remove the data just extracted
        except IndexError:
            raw_packet = data   # Case where remaining data is less than a packet
            data = []           # set the data to an empty list to break from loop.

        checksum = hashlib.md5(raw_packet).digest()  # creates unique 16-byte hash value from raw_packet as a byte array
        seqnum = hashlib.md5(bytes(str(packet_num), 'utf-8')).digest()    # does same as above but for sequence number

        packet = seqnum + checksum + raw_packet    # Combine seqnum, checksum, & raw_packet into packet
        packets.append(packet)
        packet_num += 1

    return packets


def send_packets(sock: socket, packets: list, addr_and_port: tuple):
    """
    Send a collection of packets to a destination address through a socket.

    :param sock:            The socket object through which the packets will be sent
    :param packets:         The collection of packets.
    :param addr_and_port:   A tuple containing the destination address and destination port number
    :param data_percent_loss:    The probability that we should lose the data the sender gets from the receiver
    :param seqnum_percent_loss:    The probability that we should corrupt the ack the sender gets from the receiver

    :return:                None
    """
    cur_packet_num = 0      # The number of the current packet being sent
    while cur_packet_num < len(packets):
        logging.debug(f"SEND_PACKETS: inside for loop for packet {str(cur_packet_num)}")
        seqnum, checksum, data = parse_packet(packets[cur_packet_num])   # Parse the packet being sent so the response can be compared
        sock.sendto(packets[cur_packet_num], addr_and_port)  # Send the packet.

        # Process ack and checksum from receiver
        try:
            received_data = sock.recv(CHECKSUM_SIZE + SEQNUM_SIZE)      # Receive an ack (seqnum)
            recvd_seqnum, recvd_checksum, recvd_data = parse_packet(received_data)

            if received_data == TERMINATE:      # break out of the loop upon receiving terminate
                break
        except:    # A timeout (probably) occurred; go to the top of the loop
            logging.error('SEND_PACKETS: timeout occured')
            continue

        logging.debug(f'SEND_PACKETS: received data: {received_data}')

        if (recvd_seqnum == seqnum) and (recvd_checksum == checksum):   # Case 1: both seqnum and checksum are verified
            logging.debug(f"SEND_PACKETS: seqnum and checksum received for packet {str(cur_packet_num)}")
            cur_packet_num += 1
        elif recvd_seqnum != seqnum:
            logging.error(f"SEND_PACKETS ERROR: Invalid seqnum from packet {str(cur_packet_num)}, resend data")
        else:
            logging.error(f"SEND_PACKETS ERROR: Invalid checksum from packet {str(cur_packet_num)}, resend data")

    logging.info('SEND_PACKETS: Transmission complete\n')


def parse_packet(raw_data: bytes) -> tuple:
    """
    From a string of raw data, extract the sequence number, checksum, and data. Return these values in a tuple.

    :param raw_data:    The raw data to parse.

    :return: A tuple containing the sequence number, checksum, and packet contents
    """

    seqnum = raw_data[:SEQNUM_SIZE]
    checksum = raw_data[SEQNUM_SIZE:SEQNUM_SIZE + CHECKSUM_SIZE]
    data = raw_data[SEQNUM_SIZE + CHECKSUM_SIZE:]

    return seqnum, checksum, data


def receive_packets(sock: socket, data_percent_corrupt=0, seqnum_percent_corrupt=0,
                    data_percent_loss=0, seqnum_percent_loss=0) -> tuple:
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.
    :param data_percent_corrupt:    The probability that we should corrupt the data the receiver gets from the sender
    :param seqnum_percent_corrupt:    The probability that we should corrupt the ack the receiver gets from the sender

    :return:        the packets along with the address of the sender
    """
    packets = []
    packets_received = 0
    num_packets = 0
    prev_ack = b''
    while True:
        raw_data, return_address = sock.recvfrom(4096)  # Receive a packet
        seqnum, checksum, data = parse_packet(raw_data)  # Obtain the seqnum, checksum, and data from the packet

        if lose_seqnum(seqnum_percent_loss) or lose_checksum(data_percent_loss):  # do nothing if packet shouldnt be sent back
            continue
        if packets_received == 0:   # The init was received
            num_packets = int(data)     # store the number of packets to be received

        logging.debug(f"RECEIVE_PACKETS: ACK = {str(seqnum)}")

        # Provide a chance to corrupt the sequence number if the probability is > 0.
        seqnum = corrupt_ack(seqnum, seqnum_percent_corrupt)
        seqnum_check = hashlib.md5(bytes(str(packets_received), 'utf-8')).digest()

        if seqnum_check != seqnum:  # Case 1: The sequence number isnt the desired one
            logging.error(f"RECEIVE_PACKETS ERROR: ACK  {str(seqnum_check)} invalid for packet {str(packets_received)}")
            sock.sendto(prev_ack, return_address)

        else:   # Case 2: the sequence number is correct
            checksum_check = hashlib.md5(data).digest()  # Create hash for the current packet's data
            checksum_check = corrupt_checksum(checksum_check, data_percent_corrupt)  # chance to corrupt checksum

            if checksum_check != checksum:  # Sub-case 1: The data was corrupted
                logging.error(f"RECEIVE_PACKETS ERROR: packet {str(packets_received)} checksum mismatch")
                sock.sendto(prev_ack, return_address)

            else:   # Sub-case 2: The data is intact
                if packets_received > 0:
                    packets.append(data)  # Successful, add the received packet to a list and repeat.
                logging.debug("RECEIVE_PACKETS: Received packet successfully")
                prev_ack = seqnum + checksum
                sock.sendto(prev_ack, return_address)   # Send response back to sender when everything is correct
                packets_received += 1

                if packets_received == num_packets:     # Once all packets have been received, signal sender to stop
                    logging.info("RECEIVE_PACKETS: Finished receiving packets")
                    sock.sendto(TERMINATE, return_address)
                    return packets, return_address


def corrupt_checksum(checksum: bytes, probability: float) -> bytes:
    """
    Will corrupt a packet with a certain probability less than 1.
    :param checksum:            The input packet
    :param probability:     The likelihood that the packet will be corrupted
    :return checksum:           The corrupted checksum
    """
    if probability == 0:
        # If corruption probability is 0, simply return the checksum
        return checksum

    assert(0 <= probability < 1)
    probability *= 100      # Turn the percentage into an integer
    rand_num = rnd.randint(0, 100)
    if probability > rand_num:      # return an invalid checksum
        logging.debug("packet corrupted!")
        first_half = checksum[:int(CHECKSUM_SIZE / 2)]
        second_half = checksum[int(CHECKSUM_SIZE / 2):]
        return second_half + first_half
    else:   # return original checksum
        return checksum


def corrupt_ack(ack_bit: int, probability: float) -> int:
    if probability == 0:
        # If corruption probability is 0 then simply return the ack bit
        return ack_bit

    assert (0 <= probability < 1)
    probability *= 100  # Turn the percentage into an integer
    rand_num2 = rnd.randint(0, 100)
    if probability > rand_num2:
        logging.debug("ack corrupt!")
        first_half = ack_bit[:int(SEQNUM_SIZE / 2)]
        second_half = ack_bit[int(SEQNUM_SIZE / 2):]
        return second_half + first_half
    else:
        return ack_bit


def lose_checksum(probability: float) -> bool:
    """
    Will corrupt a packet with a certain probability less than 1.
    :param probability:     The likelihood that the packet will be corrupted
    """
    if probability == 0:
        # If corruption probability is 0, simply return the checksum
        return False

    assert(0 <= probability < 1)
    probability *= 100      # Turn the percentage into an integer
    rand_num = rnd.randint(0, 100)
    if probability > rand_num:      # return an invalid checksum
        logging.debug("packet lost!")
        return True
    else:
        return False


def lose_seqnum(probability: float) -> bool:
    """
    Will corrupt a packet with a certain probability less than 1.
    :param probability:     The likelihood that the packet will be corrupted
    """
    if probability == 0:
        # If corruption probability is 0, simply return the checksum
        return False

    assert(0 <= probability < 1)
    probability *= 100      # Turn the percentage into an integer
    rand_num = rnd.randint(0, 100)
    if probability > rand_num:      # return an invalid checksum
        logging.debug("seqnum lost!")
        return True
    else:
        return False
