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
logging.basicConfig(level=logging.DEBUG)

SEQNUM_SIZE = 16        # Size of sequence number in bytes.
CHECKSUM_SIZE = 16      # Size of checksum in bytes.
PACKET_SIZE = 2048      # Size of a packet in bytes.

WINDOW_SIZE = 100        # The size of a window for go-back-n protocol
#TIMEOUT = .06           # the timeout period of gbn in milliseconds

INITIALIZE = b'\r\n'    # The terminator character sequence.
TERMINATE = b'\n\r'     # The terminator character sequence.


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
    acked_packets = 0      # The number of the current packet being sent
    window = []
    timeout_period = .00001
    next_seqnum = 0
    base = 0
    ref_time = time.time()
    while acked_packets < len(packets) or len(window) > 0:

        if next_seqnum < base + WINDOW_SIZE and acked_packets < len(packets) + 1:
            try:
                seqnum, checksum, data = parse_packet(packets[next_seqnum])      # Parse the packet being sent so the response can be compared
            except:
                print("DONE")
                return
            sock.sendto(packets[next_seqnum], addr_and_port)                 # Send the packet.
            logging.debug(f"SEND_PACKETS: packet sent")
            window.append(packets[next_seqnum])                     # The packet just sent gets added to the window
            next_seqnum += 1                                        # Increment the next seqnum pointer

        # Process ack and checksum from receiver
        try:
            received_data = sock.recv(CHECKSUM_SIZE + SEQNUM_SIZE)      # Receive an ack (seqnum)
            recvd_seqnum, recvd_checksum, recvd_data = parse_packet(received_data)
            if received_data == TERMINATE:      # break out of the loop upon receiving terminate
                break

            checksum_chk = get_hash(int_to_bytes_padded(recvd_seqnum))      # checksum of the received sequence number

            if checksum_chk == recvd_checksum:    # The data is valid
                while recvd_seqnum > base and len(window) > 0:   # move up the base
                    ref_time = time.time()      # reset the timer
                    window.pop(0)               # remove the packet at the current base
                    base += 1                   # slide the window up

        except:    # A timeout occurred; check if it was the main timer that expired
            if time.time()-ref_time > 10*timeout_period:
                #logging.error('SEND_PACKETS: resending the window')
                for packet in window:
                    sock.sendto(packet, addr_and_port)
    print('DONE')

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
    expected_seqnum = 0
    prev_ack = b''
    append_packet = True
    while True:
        append_packet = True
        raw_data, return_address = sock.recvfrom(4096)  # Receive a packet
        rcvd_seqnum, rcvd_checksum, data = parse_packet(raw_data)  # Obtain the rcvd_seqnum, rcvd_checksum, and data from the packet

        if lose_seqnum(seqnum_percent_loss) or lose_checksum(data_percent_loss):  # do nothing if packet shouldnt be sent back
            continue
        if packets_received == 0:   # The init was received
            num_packets = int(data)     # store the number of packets to be received
            packets_received += 1
            append_packet = False

        logging.debug(f"RECEIVE_PACKETS: ACK = {str(rcvd_seqnum)}")
        # Provide a chance to corrupt the sequence number if the probability is > 0.
        rcvd_seqnum = corrupt_ack(rcvd_seqnum, seqnum_percent_corrupt)
        rcvd_checksum = corrupt_checksum(rcvd_checksum, data_percent_corrupt)

        seqnum_check = get_hash(packets_received)

        rcvd_data_checksum = get_hash(data)
        if rcvd_data_checksum == rcvd_checksum:  # verify rcvd_checksum

            if expected_seqnum == rcvd_seqnum:  # store the packet if it was the expected packet in the order
                if append_packet:
                    packets.append(data)    # only append the packet if it isnt the init packet
                seqnum = int_to_bytes_padded(expected_seqnum)
                checksum = get_hash(seqnum)
                sock.sendto((seqnum + checksum), return_address)
                expected_seqnum += 1
            else:
                seqnum = int_to_bytes_padded(expected_seqnum)
                checksum = get_hash(seqnum)
                sock.sendto((seqnum + checksum), return_address)
        else:
            pass

        if expected_seqnum == num_packets:  # Once all packets have been received, signal sender to stop
            logging.info("RECEIVE_PACKETS: Finished receiving packets")
            sock.sendto(TERMINATE, return_address)
            return packets, return_address


def get_hash(item):
    if isinstance(item, int):
        return hashlib.md5(bytes(str(item), 'utf-8')).digest()
    elif isinstance(item, bytes):
        return hashlib.md5(item).digest()
    elif isinstance(item, str):
        return hashlib.md5(bytes(item), 'utf-8').digest()


def int_to_bytes_padded(num):
    packet_num_digits = len(str(num))  # get the number of packet_num digits (length of it)
    seqnum = ''.join(['0' for _ in range(SEQNUM_SIZE - packet_num_digits)]) + str(num)
    seqnum = bytes(seqnum, 'utf-8')
    return seqnum


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
        seqnum = int_to_bytes_padded(packet_num)

        packet = seqnum + checksum + raw_packet    # Combine rcvd_seqnum, checksum, & raw_packet into packet
        packets.append(packet)
        packet_num += 1

    return packets


def parse_packet(raw_data: bytes) -> tuple:
    """
    From a string of raw data, extract the sequence number, checksum, and data. Return these values in a tuple.

    :param raw_data:    The raw data to parse.

    :return: A tuple containing the sequence number, checksum, and packet contents
    """

    seqnum = int(raw_data[:SEQNUM_SIZE])
    checksum = raw_data[SEQNUM_SIZE:SEQNUM_SIZE + CHECKSUM_SIZE]
    data = raw_data[SEQNUM_SIZE + CHECKSUM_SIZE:]

    return seqnum, checksum, data


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


def corrupt_ack(seqnum: bytes, probability: float) -> bytes:
    if probability == 0:
        # If corruption probability is 0 then simply return the ack bit
        return seqnum

    assert (0 <= probability < 1)
    probability *= 100  # Turn the percentage into an integer
    rand_num2 = rnd.randint(0, 100)
    if probability > rand_num2:
        #logging.debug("ack corrupt!")
        #first_half = seqnum[:int(SEQNUM_SIZE / 2)]
        #second_half = seqnum[int(SEQNUM_SIZE / 2):]
        #return second_half + first_half
        if int(seqnum) == 0:
            return int_to_bytes_padded(1)
        else:
            return int_to_bytes_padded(int(int(seqnum)/2))
    else:
        return seqnum


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
