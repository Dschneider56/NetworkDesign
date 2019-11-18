from socket import *
from time import sleep
import random as rnd
import logging
from threading import Thread
import datetime as dt

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

"""
To enable debugging statements, change the below level value to logging.DEBUG
To disable them, change level to logging.CRITICAL
"""

logging.basicConfig(level=logging.DEBUG)  # For print statements, change CRITICAL to DEBUG. To disable them,
# change DEBUG to CRITICAL.

SEQNUM_SIZE = 1  # Size of sequence number in bytes.
CHECKSUM_SIZE = 24  # Size of checksum in bytes.
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
    packets: list = []
    seqnum = int(0)
    while len(data) > 0:  # Keep appending the packets to the packet list.
        try:
            raw_packet = data[:PACKET_SIZE]  # Extract the first "PACKET_SIZE" bytes into packet.
            data = data[PACKET_SIZE:]
        except IndexError:
            raw_packet = data  # Case where remaining data is less than a packet
            data = []  # set the data to an empty list to break from loop.

        checksum = bytes(format(sum(raw_packet), '024b'), 'utf-8')  # Create a checksum for the packet.

        seqnum = bytes(str(seqnum ^ 1), 'utf-8')  # Create an alternating sequence number. Note the
        # cast to bytes requires a string object.

        packet = raw_packet + checksum + seqnum  # Combine seqnum, checksum, & raw_packet into packet
        packets.append(packet)

        seqnum = int(seqnum)  # Cast back to int so XOR operation can be done again.
    return packets


def parse_packet(raw_data: bytes) -> tuple:
    """
    From a string of raw data, extract the sequence number, checksum, and data. Return these values in a tuple.

    :param raw_data:    The raw data to parse.

    :return: A tuple containing the sequence number, checksum, and packet contents
    """

    seqnum = raw_data[-SEQNUM_SIZE:]
    checksum = raw_data[-CHECKSUM_SIZE - SEQNUM_SIZE:-SEQNUM_SIZE]
    data = raw_data[:(- CHECKSUM_SIZE - SEQNUM_SIZE)]

    return data, checksum, seqnum


def receive_packets(sock: socket, data_percent_corrupt=0, ack_percent_corrupt=0) -> tuple:
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.
    :param data_percent_corrupt:    The probability that we should corrupt the data the receiver gets from the sender
    :param ack_percent_corrupt:    The probability that we should corrupt the ack the receiver gets from the sender


    :return:        the packets along with the address of the sender
    """
    packets = []
    packets_received = 0
    num_packets = 0
    previous_acknowledgement = bytes(str(0), 'utf-8') + (bytes("000000000000000000000000", 'utf-8'))
    while True:
        logging.debug("RECEIVE_PACKETS: waiting")
        raw_data, return_address = sock.recvfrom(4096)  # Receive a packet
        logging.debug(f"RECEIVED PACKET: {raw_data}")

        if raw_data[:7] == bytes(str(INITIALIZE),
                                 'utf-8'):  # If the INITIALIZE character sequence is received, set up for loop.
            logging.debug("RECEIVED INITIALIZATION STATEMENT")
            # store the number of packets to be received
            num_packets = int(raw_data[7:-25])

        ack = packets_received % 2
        packets_received += 1

        logging.debug("RECEIVER: ACK = " + str(ack))

        # This line is used to test ack packet bit errors. This corrupts the ack so the receiver will wait for a timeout
        # The default percentage of corruption is 0, so this is essentially a no-op unless told to corrupt
        ack = corrupt_ack(ack, ack_percent_corrupt)

        data, checksum, seqnum = parse_packet(raw_data)

        if ack != int(seqnum):
            logging.debug("Receiver: Error, ack " + str(ack) + " is invalid for packet " + str(packets_received))
            # Decrement packets_receiver and then do nothing (wait for a timeout)
            sock.sendto(previous_acknowledgement, return_address)
            packets_received -= 1

        else:
            # Convert new checksum into a string
            new_checksum = str(bytes(format(sum(data[:PACKET_SIZE]), '024b'), 'utf-8'))

            # Swap the 1's and 0's of the new checksum
            new_checksum = new_checksum.replace('0', 'x')
            new_checksum = new_checksum.replace('1', '0')
            new_checksum = new_checksum.replace('x', '1')

            # Filter out the extra "b'" and "'" in the new string
            new_checksum = new_checksum[2:len(new_checksum) - 1]

            # Convert new_checksum back to bytes
            new_checksum = bytes(new_checksum, 'utf-8')

            # Sum checksum and new_checksum together, expected value is all 1's.
            result = int(checksum) + int(new_checksum)
            result = str(result)

            logging.debug(checksum)
            logging.debug(new_checksum)
            logging.debug("RESULT: " + result)

            # This line is used to test packet bit errors. This corrupts the checksum so the receiver will wait for a
            # timeout. The default percentage of corruption is 0, so this is essentially a no-op unless told to corrupt
            result = corrupt_checksum(result, data_percent_corrupt)

            if result != "111111111111111111111111":
                logging.debug("Error, checksums do not match for packet " + str(packets_received))
                # Decrement packets_receiver and then do nothing (wait for a timeout)
                packets_received -= 1

            else:
                packets.append(data)  # Add the received packet to a list and repeat.
                # Send response back to sender when everything is correct
                logging.debug("Packet received successfully, sending response to sender")
                sock.sendto(bytes(str(ack), 'utf-8') + (bytes(result, 'utf-8')), return_address)
                previous_acknowledgement = bytes(str(ack), 'utf-8') + (bytes(result, 'utf-8'))
                if packets_received == num_packets:
                    logging.debug("Finished receiving packets -------------------------")
                    sock.sendto(TERMINATE, return_address)
                    return packets, return_address


def corrupt_checksum(checksum: str, probability: float) -> str:
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
    if probability > rand_num:
        logging.debug("packet corrupted!")
        # return an invalid checksum
        return "000000000000000000000000"
    else:
        # return original checksum
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
        return 2
    else:
        return ack_bit
