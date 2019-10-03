from socket import *

PACKET_SIZE = 1024
TERMINATE = b'\r\n'


def send_packets(sock: socket, packets: list, addr_and_port):
    for packet in packets:
        print(packet)
        sock.sendto(packet, addr_and_port)       # Send the packet
        #print(f'From CLIENT to SERVER: {packet}')
        sock.recvfrom(len(TERMINATE))                # Await an ACK

    sock.sendto(TERMINATE, addr_and_port)    # Every packet has been sent, signal the recipient to stop listening
    sock.recvfrom(len(TERMINATE))


def receive_packets(sock: socket):
    packets = []
    while True:
        print('inside receive_packets')
        message, return_address = sock.recvfrom(PACKET_SIZE)
        if message == TERMINATE:
            print('received terminate')
            return packets, return_address
        else:
            print('recieved a packet')
            packets.append(message)
        # return packets, return_address if message == TERMINATE else packets.append(message)


def make_packet(data):
    packets: list = []
    while len(data) >= PACKET_SIZE:
        packets.append(data[:PACKET_SIZE])
        data = data[PACKET_SIZE:]
        #print(packets[-1])
    packets.append(data[:-1])
    #packets.append(TERMINATE)
    #print(packets[-1])
    return packets