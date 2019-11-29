import math
from socket import *
import random as rnd
import logging

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

"""
To enable debugging statements, change the below level value to logging.DEBUG
To disable them, change level to logging.CRITICAL
"""

logging.basicConfig(level=logging.DEBUG)  # For print statements, change CRITICAL to DEBUG. To disable them,
# change DEBUG to CRITICAL.

CHECKSUM_SIZE = 24  # Size of checksum in bytes.
PACKET_SIZE = 2048  # Size of a packet in bytes.
INITIALIZE = b'\r\n'  # The terminator character sequence.
TERMINATE = b'\n\r'  # The terminator character sequence.

# class Timer:
#     def __init__(self, period, on_timeout, on_receive):
#         self.period = period
#         self.on_timeout = on_timeout
#         timer_thread = Thread(target=self.time_elapsed)
#
#     def time_elapsed(self):
#         start_time = dt.datetime.now()
#         end_time = start_time + self.period
#         while dt.datetime.now() < end_time:
#             sleep(0.001)
#         self.on_timeout(True)


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a certain size containing the data, a checksum,
    and a sequence number.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    num_packets = math.ceil(len(data) / 2048) + 1
    seqnum = int(0)
    while seqnum <= num_packets:
        if len(data) > PACKET_SIZE:  # Keep appending the packets to the packet list.
            raw_packet = data[:PACKET_SIZE]  # Extract the first "PACKET_SIZE" bytes into packet.
            data = data[PACKET_SIZE:]
        elif len(data) > 0:
            raw_packet = data  # Case where remaining data is less than a packet
            data = []  # set the data to an empty list to break from loop.
        else:
            return packets
        seqnum += 1     # Start seq number at 1 since initializer will be added with seq number 0
        checksum = bytes(format(sum(raw_packet), '024b'), 'utf-8')  # Create a checksum for the packet.

        seqnum = bytes(str(seqnum), 'utf-8')  # Keep track of sequence number.

        while len(seqnum) < len(bytes(str(num_packets), 'utf-8')):  # Make sure sequence number is proper length
            seqnum = b'0' + seqnum      # Append 0's to sequence number so length is correct for parsing

        packet = raw_packet + checksum + seqnum  # Combine raw_packet, checksum and seqnum into packet
        packets.append(packet)      # Add packet to list of packets

        seqnum = int(seqnum)  # Cast back to int so it can be incremented again


def send_packets(sock: socket, packets: list, addr_and_port: tuple, data_percent_loss=0, ack_percent_loss=0):
    """
    Send a collection of packets to a destination address through a socket.

    :param sock:            The socket object through which the packets will be sent
    :param packets:         The collection of packets.
    :param addr_and_port:   A tuple containing the destination address and destination port number
    :param data_percent_loss:    The probability that we should lose the data the sender gets from the receiver
    :param ack_percent_loss:    The probability that we should corrupt the ack the sender gets from the receiver

    :return:                None
    """

    logging.debug("Sending initialization statement:")

    # Create an initialize statement and append the number of packets the receiver should expect
    # len(packets) is the number of packets of data we send, and we add 1 for the initializer
    initializer = bytes(str(INITIALIZE), 'utf-8')
    logging.debug("INITIALIZER ----------------------")

    checksum = bytes(format(sum(initializer), '024b'), 'utf-8')  # Create a checksum for the initializer.

    # Initializer will send over the number of packets at the end, as opposed to a sequence number
    num_packets = bytes(str(len(packets) + 1), 'utf-8')

    # Combine seqnum, checksum, & initializer into a packet
    initializer_packet = initializer + checksum + num_packets
    seq_num_size = len(bytes(str(len(packets) + 1), 'utf-8'))       # Seq_num_size determined by the number of packets
    # Including the initializer

    packets.insert(0, initializer_packet)  # Append the initializer to the start of our list of packets

    # Done creating and appending initializer

    # i is the index of our packets list which we will use to send packets in the proper order.
    i = 0
    while i < len(packets):     # While we still have packets to send, send over a packet one at a time
        logging.debug("SEND_PACKETS: inside for loop for packet " + str(i + 1))
        ack = i
        received_ack = -1
        received_checksum = -1
        sock.sendto(packets[i], addr_and_port)  # Send the packet.

        # Process ack and checksum from receiver
        try:
            # Receive an ack
            received_data, return_address = sock.recvfrom(CHECKSUM_SIZE + seq_num_size)
            if received_data == TERMINATE:
                i = len(packets)
                continue
            received_ack = int(received_data[:seq_num_size])
            received_checksum = str(received_data[seq_num_size:])
        except Exception as e:
            logging.debug(e)
            continue

        logging.debug(f'SENDER: received data: {received_data}')

        # If instructed to corrupt data do so, otherwise do nothing for these next 2 lines
        received_checksum = corrupt_checksum(received_checksum, data_percent_loss)
        received_ack = corrupt_ack(received_ack, ack_percent_loss)

        if (received_ack == ack) and (received_checksum == "b'111111111111111111111111'"):
            logging.debug("SENDER: Correct ACK and Checksum received for packet " + str(i + 1))
            i += 1
        elif received_ack != ack:
            logging.debug("SENDER: invalid ack from packet " + str((i + 1)) + ", resending data")
            # If ack does not change resend that packet

        else:
            logging.debug("SENDER: Invalid checksum received from packet " + str((i + 1)) + ", resending data")
            # If checksum is incorrect, subtract 1 from i and resend that packet
    logging.debug('COMPLETE\n')


def parse_packet(raw_data: bytes, seq_num_size) -> tuple:
    """
    From a string of raw data, extract the sequence number, checksum, and data. Return these values in a tuple.

    :param raw_data:    The raw data to parse.

    :param seq_num_size:    The size of the sequence number, needed to properly parse data

    :return: A tuple containing the sequence number, checksum, and packet contents
    """

    seqnum = raw_data[-seq_num_size:]
    checksum = raw_data[-CHECKSUM_SIZE - seq_num_size:-seq_num_size]
    data = raw_data[:(- CHECKSUM_SIZE - seq_num_size)]

    # TODO: If statement should be replaced when implementing a handshake for the TCP connection
    if data == bytes(str(INITIALIZE), 'utf-8'):
        seqnum = b'0'   # Initializer has a seqnum of the number of packets.
        # If data received is the initializer we know to set the sequence number to 0

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

        # TODO: This should be replaced once the handshake is implemented
        if raw_data[:7] == bytes(str(INITIALIZE),
                                 'utf-8'):  # If the INITIALIZE character sequence is received, set up for loop.
            logging.debug("RECEIVED INITIALIZATION STATEMENT")
            # store the number of packets to be received
            num_packets = int(raw_data[31:])    # 31 is len(Initializer) + len(checksum) - 1 since starting index is 0

        seq_num_size = len(bytes(str(num_packets), 'utf-8'))
        ack = packets_received
        packets_received += 1

        logging.debug("RECEIVER: ACK = " + str(ack))

        # This line is used to test ack packet bit errors. This corrupts the ack so the receiver will wait for a timeout
        # The default percentage of corruption is 0, so this is essentially a no-op unless told to corrupt
        ack = corrupt_ack(ack, ack_percent_corrupt)

        ack = bytes(str(ack), 'utf-8')  # Keep track of sequence number.
        while len(ack) < seq_num_size:  # Make sure ack is proper size for parsing by the sender
            ack = b'0' + ack

        data, checksum, seqnum = parse_packet(raw_data, seq_num_size)

        if int(ack) != int(seqnum):
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
                sock.sendto(ack + (bytes(result, 'utf-8')), return_address)
                previous_acknowledgement = ack + (bytes(result, 'utf-8'))
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
