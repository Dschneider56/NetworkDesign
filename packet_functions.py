from socket import *
import random as rnd
import logging
import math
import time

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

"""
To enable debugging statements, change the below level value to logging.DEBUG
To disable them, change level to logging.CRITICAL
"""
logging.basicConfig(level=logging.CRITICAL)  # For print statements, change CRITICAL to DEBUG. To disable them,
                                            # change DEBUG to CRITICAL.

SEQNUM_SIZE = 16  # Size of sequence number in bytes.
CHECKSUM_SIZE = 24  # Size of checksum in bytes.
PACKET_SIZE = 2048  # Size of a packet in bytes.
INITIALIZE = b'\r\n'  # The terminator character sequence.
TERMINATE = b'\n\r'  # The terminator character sequence.
WINDOW_SIZE = 10


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

        checksum = bytes(format(sum(raw_packet), '024b'), 'utf-8')  # Create a checksum for the packet.
        seqnum = packet_num.to_bytes(16, "little")  # Keep track of sequence number.

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

    :return:                None
    """
    base = 0

    while base < len(packets) + 1:

        # Send a window of packets to the receiver
        for next_sequence_num in range(base, base + WINDOW_SIZE + 1):
            if next_sequence_num < len(packets):
                sock.sendto(packets[next_sequence_num], addr_and_port)  # Send the packet.

        # Receive a window of packets
        exit_loop = False
        reference_time = time.time()
        for next_sequence_num in range(base, base + WINDOW_SIZE + 1):
            if exit_loop:
                break
            if next_sequence_num < len(packets):
                try:
                    received_data = sock.recv(CHECKSUM_SIZE + SEQNUM_SIZE)      # Receive an ack (seqnum)
                    if received_data == b'':
                        exit_loop = True
                        break

                    recvd_seqnum, recvd_checksum, recvd_data = parse_packet(received_data)
                    recvd_seqnum = int.from_bytes(recvd_seqnum, "little")

                    logging.debug(f'SEND_PACKETS: received data: {received_data}')

                    base = int(recvd_seqnum) + 1   # does same as above but for sequence number
                    reference_time = time.time()

                    if base >= len(packets):
                        # Once the receiver has gotten all of the packets, send a terminator and exit the loop
                        sock.sendto(TERMINATE, addr_and_port)
                        return

                except:    # A timeout occurred; go to the top of the while loop
                    logging.error('SEND_PACKETS: timeout occured')
                    if (time.time() - reference_time) > 0.01:
                        exit_loop = True
                    continue


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
    :param data_percent_loss:    The probability that we should drop the data the receiver gets from the sender
    :param seqnum_percent_loss:    The probability that we should drop the ack the receiver gets from the sender

    :return:        the packets along with the address of the sender
    """
    packets = []
    packets_received = 0
    num_packets = 0
    prev_ack = b''
    while True:
        raw_data, return_address = sock.recvfrom(4096)  # Receive a packet
        seqnum, checksum, data = parse_packet(raw_data)  # Obtain the seqnum, checksum, and data from the packet

        if raw_data == TERMINATE:  # Once all packets have been received, signal sender to stop
            logging.info("RECEIVE_PACKETS: Finished receiving packets")
            return packets, return_address

        if lose_seqnum(seqnum_percent_loss) or lose_checksum(data_percent_loss):  # do nothing if packet shouldnt be sent back
            continue

        seqnum = int.from_bytes(seqnum, "little")
        logging.debug(f"RECEIVE_PACKETS: ACK = {str(seqnum)}")

        # Provide a chance to corrupt the sequence number if the probability is > 0.
        seqnum = corrupt_ack(seqnum, seqnum_percent_corrupt)

        if packets_received != seqnum:  # Case 1: The sequence number isnt the desired one
            logging.error(f"RECEIVE_PACKETS ERROR: ACK  {str(seqnum)} invalid for packet {str(packets_received)}")
            sock.sendto(prev_ack, return_address)

        else:   # Case 2: the sequence number is correct
            checksum = corrupt_checksum(checksum, data_percent_corrupt)  # chance to corrupt checksum
            checksum_check = bytes(format(sum(data), '024b'), 'utf-8')  # Create a checksum for the packet.

            if checksum_check != checksum:  # Sub-case 1: The data was corrupted
                logging.error(f"RECEIVE_PACKETS ERROR: packet {str(packets_received)} checksum mismatch")
                sock.sendto(prev_ack, return_address)

            else:   # Sub-case 2: The data is intact
                if packets_received > 0:
                    packets.append(data)  # Successful, add the received packet to a list and repeat.
                logging.debug("RECEIVE_PACKETS: Received packet number " + str(packets_received) + " successfully")
                prev_ack = seqnum.to_bytes(16, "little") + checksum
                sock.sendto(prev_ack, return_address)   # Send response back to sender when everything is correct
                packets_received += 1


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
        return bytes(checksum + b'2')
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
        return -ack_bit
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
