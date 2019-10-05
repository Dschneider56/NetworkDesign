from socket import *

PACKET_SIZE = 1024
TERMINATE = b'\r\n'


def send_packets(sock: socket, packets: list, addr_and_port):
    for packet in packets:
        print(packet)
        sock.sendto(packet, addr_and_port)       # Send the packet

    print("Sending terminate statement:")
    sock.sendto(TERMINATE, addr_and_port)    # Every packet has been sent, signal the recipient to stop listening


def receive_packets(sock: socket):
    packets = []
    while True:
        message, return_address = sock.recvfrom(PACKET_SIZE)
        if message == TERMINATE:
            print('Received terminate statement')
            return packets, return_address
        else:
            print('\nPacket received:')
            packets.append(message)
            print(message)
        # return packets, return_address if message == TERMINATE else packets.append(message)


def make_packet(data):
    packets: list = []
    while len(data) >= PACKET_SIZE:
        packets.append(data[:PACKET_SIZE])
        data = data[PACKET_SIZE:]
    packets.append(data)
    return packets
