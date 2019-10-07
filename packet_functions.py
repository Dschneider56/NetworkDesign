from socket import *
from time import sleep


# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.
PACKET_SIZE = 2048      # Size of a packet in bytes.
TERMINATE = b'\r\n'     # The terminator character sequence.


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
        sleep(0.0001)                           # Small delay so receiver is not overloaded.

    # print("Sending terminate statement:")
    sock.sendto(TERMINATE, addr_and_port)    # Every packet has been sent, signal the recipient to stop listening.


def receive_packets(sock: socket):
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.

    :return:        None
    """
    packets = []
    while True:
        message, return_address = sock.recvfrom(PACKET_SIZE)    # Receive a chunk of data of up to size 'PACKET_SIZE'.

        if message == TERMINATE:    # If the TERMINATE character sequence is received, then the transition is complete.
            # print('Received terminate statement')
            return packets, return_address
        else:
            # print('\nPacket received:')
            packets.append(message)     # Add the received packet to a list and repeat.
            # print(message)


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a specified size.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    while len(data) >= PACKET_SIZE:             # Keep appending the packets to the packet list
        packets.append(data[:PACKET_SIZE])      # Take up to 'PACKET_SIZE' bytes and add that packet to a list
        data = data[PACKET_SIZE:]               # Remove that data from the buffer and repeat above step
    packets.append(data)        # Append whatever is left at the end.
    return packets
