from socket import *
from time import sleep
import random as rnd
import logging

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

"""
To enable debugging statements, change the below level value to logging.DEBUG
To disable them, change level to logging.CRITICAL
"""

logging.basicConfig(level=logging.CRITICAL)     # For print statements, change CRITICAL to DEBUG. To disable them,
                                                # change DEBUG to CRITICAL.

SEQNUM_SIZE = 1         # Size of sequence number in bytes.
CHECKSUM_SIZE = 24        # Size of checksum in bytes.
PACKET_SIZE = 2048      # Size of a packet in bytes.
INITIALIZE = b'\r\n'     # The terminator character sequence.
ACK = b'\r\n'


def send_packets(sock: socket, packets: list, addr_and_port: tuple, data_percent_corrupt=0.0):
    """
    Send a collection of packets to a destination address through a socket.

    :param sock:            The socket object through which the packets will be sent
    :param packets:         The collection of packets.
    :param addr_and_port:   A tuple containing the destination address and destination port number

    :return:                None
    """

    # logging.debug("Sending initialization statement:")

    initializer = bytes(str(INITIALIZE) + str(len(packets)), 'utf-8')
    logging.debug("INITIALIZER ----------------------")
    sock.sendto(initializer, addr_and_port)  # Every packet has been sent, signal the recipient to stop listening.
    sleep(0.01)
    i = 0
    while i < len(packets):
        logging.debug("SEND_PACKETS: inside for loop " + str(i))
        ack = (i + 1) % 2
        received_ack = -1
        packet = corrupt_packet(packets[i], data_percent_corrupt)
        sock.sendto(packet, addr_and_port)      # Send the packet.

        # Process ack and checksum from receiver
        received_data, return_address = sock.recvfrom(CHECKSUM_SIZE + SEQNUM_SIZE)  # Receive a ack

        logging.debug(f'SEND: received data: {received_data}')

        received_ack = int(received_data[:1])
        received_checksum = str(received_data[1:])

        if (received_ack == ack) and (received_checksum == "b'111111111111111111111111'"):
            logging.debug("ACK and Checksum received for packet " + str(i + 1))
            i += 1
        elif received_ack != ack:
            logging.debug("invalid ack from packet " + str((i + 1)) + ", resending data")
            # If ack does not change resend that packet

        else:
            logging.debug("Invalid checksum received from packet " + str((i + 1)) + ", resending data")
            # If checksum is incorrect, subtract 1 from i and resend that packet
    logging.debug('\n')


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


def receive_packets(sock: socket, ack_corrupt_percentage=0) -> tuple:
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.

    :return:        the packets along with the address of the sender
    """
    packets = []
    packets_received = 0
    num_packets = 0
    while True:
        logging.debug("RECEIVE_PACKETS: waiting")
        raw_data, return_address = sock.recvfrom(4096)  # Receive a packet
        logging.debug(f"RECEIVED PACKET: {raw_data}")

        if raw_data[:7] == bytes(str(INITIALIZE), 'utf-8'):    # If the INITIALIZE character sequence is received, set up for loop.
            logging.debug("RECEIVED INITIALIZATION STATEMENT")
            # store the number of packets to be received
            num_packets = int(raw_data[7:])

        else:
            packets_received += 1
            ack = corrupt_ack(packets_received % 2, ack_corrupt_percentage)
            logging.debug("ACK = " + str(ack))
            data, checksum, seqnum = parse_packet(raw_data)

            if ack != int(seqnum):
                logging.debug("Error, ack " + str(ack) + " is invalid for packet " + str(packets_received))
                # Send response to sender when ack is incorrect
                result = '0'
                sock.sendto(bytes(str(ack), 'utf-8') + bytes(result, 'utf-8'), return_address)
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

                if result != "111111111111111111111111":
                    logging.debug("Error, checksums do not match for packet " + str(packets_received))
                    # Send response back to sender for invalid checksum
                    sock.sendto(bytes(str(ack), '-utf-8') + (bytes(result, 'utf-8')), return_address)
                    packets_received -= 1

                else:
                    packets.append(data)     # Add the received packet to a list and repeat.
                    # Send response back to sender when everything is correct
                    sock.sendto(bytes(str(ack), 'utf-8') + (bytes(result, 'utf-8')), return_address)
                    if packets_received == num_packets:
                        logging.debug("Finished receiving packets -------------------------")
                        return packets, return_address


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a certain size containing the data, a checksum,
    and a sequence number.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    seqnum = int(0)
    while len(data) > 0:                                # Keep appending the packets to the packet list.
        try:
            raw_packet = data[:PACKET_SIZE]                         # Extract the first "PACKET_SIZE" bytes into packet.
            data = data[PACKET_SIZE:]
        except IndexError:
            raw_packet = data                                       # Case where remaining data is less than a packet
            data = []                                               # set the data to an empty list to break from loop.

        checksum = bytes(format(sum(raw_packet), '024b'), 'utf-8')    # Create a checksum for the packet.

        seqnum = bytes(str(seqnum ^ 1), 'utf-8')                 # Create an alternating sequence number. Note the
                                                                    # cast to bytes requires a string object.

        packet = raw_packet + checksum + seqnum                      # Combine seqnum, checksum, & raw_packet into packet
        packets.append(packet)

        seqnum = int(seqnum)                    # Cast back to int so XOR operation can be done again.
    return packets


def corrupt_packet(pack: bytes, probability: float) -> bytes:
    """
    Will corrupt a packet with a certain probability less than 1.

    :param pack:            The input packet
    :param probability:     The likelihood that the packet will be corrupted
    :return pack:           The packet that is possibly corrupted
    """
    assert(0 <= probability < 1)
    probability *= 100      # Turn the percentage into an integer
    rand_num = rnd.randint(0, 100)
    if probability > rand_num:
        logging.debug(f"packet corrupted!\nORIGINAL PACKET:   {pack}")
        pack = pack.replace(b'\x11', b'\x00')
        logging.debug(f'CORRUPTED VERSION: {pack}')
        return pack
    else:
        return pack


def corrupt_ack(ackbit: bytes, probability: float):
    assert(0 <= probability < 1)
    probability *= 100      # Turn the percentage into an integer
    rand_num2 = rnd.randint(0, 100)
    if probability > rand_num2:
        if ackbit == 1:
            return 0
        elif ackbit == 0:
            return 1
    else:
        return ackbit


# --------------------------------------- OLD FUNCTIONS BEFORE MODIFICATION ------------------------------------------ #
# To restore these functions, simply remove the _old suffix and add it to the function above to change out.

#
# def receive_packets_old(sock: socket) -> tuple:
#     """
#     Listen for packets coming in to a socket.
#
#     :param sock:    The socket that will be receiving packets.
#
#     :return:        the packets along with the address of the sender
#     """
#     packets = []
#     while True:
#         message, return_address = sock.recvfrom(PACKET_SIZE)    # Receive a chunk of data of up to size 'PACKET_SIZE'.
#
#         if message == TERMINATE:    # If the TERMINATE character sequence is received, then the transition is complete.
#             # logging.debug('Received terminate statement')
#             return packets, return_address
#         else:
#             # logging.debug('\nPacket received:')
#             packets.append(message)     # Add the received packet to a list and repeat.
#             # logging.debug(message)
#
#
# def make_packet_old(data: bytes) -> list:
#     """
#     Given a byte array, split it up into packets of a certain size containing the data, a checksum,
#     and a sequence number.
#
#     :param data:    The byte array that will be split up.
#
#     :return:        A list of packets.
#     """
#     packets: list = []
#     seqnum = 1
#     while len(data) >= PACKET_SIZE:             # Keep appending the packets to the packet list
#         packets.append(data[:PACKET_SIZE])      # Take up to 'PACKET_SIZE' bytes and add that packet to a list
#         data = data[PACKET_SIZE:]               # Remove that data from the buffer and repeat above step
#     packets.append(data)        # Append whatever is left at the end.
#     return packets
