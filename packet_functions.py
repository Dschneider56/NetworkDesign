from socket import *


# NOTE: These variables can be changed by simply altering them here. You don't need to change code anywhere else.
PACKET_SIZE = 2048      # Size of a packet in bytes.
TERMINATE = b'\r\n'     # The terminator character sequence.


def short_sleep():
    """
    Short delay to be added between packet sends.

    :return:    None
    """
    for i in range(70):
        for j in range(100):
            continue


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
        sock.sendto(packet, addr_and_port)       # Send the packet
        short_sleep()

    # print("Sending terminate statement:")
    sock.sendto(TERMINATE, addr_and_port)    # Every packet has been sent, signal the recipient to stop listening


def receive_packets(sock: socket):
    """
    Listen for packets coming in to a socket.

    :param sock:    The socket that will be receiving packets.

    :return:        None
    """
    packets = []
    while True:
        message, return_address = sock.recvfrom(PACKET_SIZE)
        if message == TERMINATE:
            # print('Received terminate statement')
            return packets, return_address
        else:
            # print('\nPacket received:')
            packets.append(message)
            # print(message)


def make_packet(data: bytes) -> list:
    """
    Given a byte array, split it up into packets of a specified size.

    :param data:    The byte array that will be split up.

    :return:        A list of packets.
    """
    packets: list = []
    while len(data) >= PACKET_SIZE:         # keep appending the packets to the packet list
        packets.append(data[:PACKET_SIZE])
        data = data[PACKET_SIZE:]
    packets.append(data)        # Append whatever is left at the end.
    return packets
