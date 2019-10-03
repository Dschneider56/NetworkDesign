from socket import *
from packet_functions import *


class Server:
    """
    awaits data from the client, and creates an image file with the data it received
    """
    def __init__(self):
        server_port = 12000         # server port number
        server_socket = socket(AF_INET, SOCK_DGRAM)
        self.data = []
        try:
            server_socket.bind(('', server_port))   # bind the socket to an address
        except Exception as e:
            print("SERVER - Server failed to initialize: {}".format(e))
            return

        print("SERVER - Server ready to receive.")
        while True:
           ##THIS WORKS!
            message, client_address = server_socket.recvfrom(PACKET_SIZE)    # receive the data and client address from client
            server_socket.sendto(TERMINATE, client_address)  # send ACK to the client
            self.data.append(message)
            if message == TERMINATE:
                print(f'server got: {self.data}')
                print("SERVER - Data received from Client: {}".format(message))

           # packets, client_address = receive_packets(server_socket)
           # print(f'server got: {self.data}')
           # send_packets(server_socket, packets, (client_address, server_port))