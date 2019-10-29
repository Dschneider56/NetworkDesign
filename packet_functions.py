from socket import *
from time import sleep

# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.

SEQNUM_SIZE = 1         # Size of sequence number in bytes.
CHKSUM_SIZE = 24        # Size of checksum in bytes.
PACKET_SIZE = 2048      # Size of a packet in bytes.
ACK = b'\r\n'     # The terminator character sequence.


def send_packets(sock: socket, packets: list, addr_and_port: tuple):
    """
    Send a collection of packets to a destination address through a socket.

    :param sock:            The socket object through which the packets will be sent
    :param packets:         The collection of packets.
    :param addr_and_port:   A tuple containing the destination address and destination port number

    :return:                None
    """
    for packet in packets:
        # print(packet)
        sock.sendto(packet, addr_and_port)      # Send the packet.
        sleep(0.01)                           # Small delay so receiver is not overloaded.

    # print("Sending terminate statement:")
    sock.sendto(ACK, addr_and_port)    # Every packet has been sent, signal the recipient to stop listening.


def parse_packet(raw_data: bytes) -> tuple:
    """
    From a string of raw data, extract the sequence number, checksum, and data. Return these values in a tuple.

    :param raw_data:    The raw data to parse.

    :return: A tuple containing the sequence number, checksum, and packet contents
    """
    seqnum = raw_data[-SEQNUM_SIZE:]
    chksum = raw_data[-CHKSUM_SIZE:-SEQNUM_SIZE]
    data = raw_data[:PACKET_SIZE]
    #print(data)
    #print(chksum)
    #print(seqnum)
    return data, chksum, seqnum


def receive_packets(sock: socket) -> tuple:
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.

    :return:        the packets along with the address of the sender
    """
    packets = []
    while True:
        raw_data, return_address = sock.recvfrom(PACKET_SIZE + CHKSUM_SIZE + SEQNUM_SIZE)  # Receive a packet

        data, chksum, seqnum = parse_packet(raw_data)

        if raw_data == ACK:    # If the TERMINATE character sequence is received, transition is complete.
            return packets, return_address
        else:
            packets.append(data)     # Add the received packet to a list and repeat.


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a certain size containing the data, a checksum,
    and a sequence number.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    seqnum = 1
    while len(data) > 0:                                # Keep appending the packets to the packet list.
        try:
            raw_packet = data[:PACKET_SIZE]                         # Extract the first "PACKET_SIZE" bytes into packet.
            data = data[PACKET_SIZE:]
        except IndexError:
            raw_packet = data                                       # Case where remaining data is less than a packet
            data = []                                               # set the data to an empty list to break from loop.

        chksum = bytes(format(sum(raw_packet), '024b'), 'utf-8')    # Create a checksum for the packet.

        seqnum = bytes(str(seqnum ^ 1), 'utf-8')                    # Create an alternating sequence number. Note the
                                                                    # cast to bytes requires a string object.

        # print(seqnum)
        # print(chksum)

        packet = raw_packet + chksum + seqnum                       # Combine seqnum, chksum, & raw_packet into packet
        packets.append(packet)

        seqnum = int(seqnum)                    # Cast back to int so XOR operation can be done again.
    return packets

# --------------------------------------- OLD FUNCTIONS BEFORE MODIFICATION ------------------------------------------ #
# To restore these functions, simply remove the _old suffix and add it to the function above to change out.


def receive_packets_old(sock: socket) -> tuple:
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.

    :return:        the packets along with the address of the sender
    """
    packets = []
    while True:
        message, return_address = sock.recvfrom(PACKET_SIZE)    # Receive a chunk of data of up to size 'PACKET_SIZE'.

        if message == ACK:    # If the TERMINATE character sequence is received, then the transition is complete.
            # print('Received terminate statement')
            return packets, return_address
        else:
            # print('\nPacket received:')
            packets.append(message)     # Add the received packet to a list and repeat.
            # print(message)


def make_packet_old(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a certain size containing the data, a checksum,
    and a sequence number.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    seqnum = 1
    while len(data) >= PACKET_SIZE:             # Keep appending the packets to the packet list
        packets.append(data[:PACKET_SIZE])      # Take up to 'PACKET_SIZE' bytes and add that packet to a list
        data = data[PACKET_SIZE:]               # Remove that data from the buffer and repeat above step
    packets.append(data)        # Append whatever is left at the end.
    return packets
