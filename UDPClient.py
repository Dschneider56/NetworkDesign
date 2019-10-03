from socket import *
from packet_functions import *
# PIL is used for image support in this program.
from PIL import Image
import base64
import io
class Client:
    """
    A client -object
    """
    def __init__(self):
        """
        Send data to some server, then request data back from the server.
        """
        server_name = '127.0.0.1'   # server address; it is the local host in this case
        server_port = 12000         # server port number
        client_socket = socket(AF_INET, SOCK_DGRAM)

        with open('sample.png', 'rb') as image:         # open the file to be transmitted
            message = image.read()

        self.packets = make_packet(message)

        send_packets(client_socket, self.packets, (server_name, server_port))

        # THIS WORKS!!
        #for packet in self.packets:
        #    client_socket.sendto(packet, (server_name, server_port))
        #    print(f'client sent: {packet}')
        #    client_socket.recvfrom(len(TERMINATE))
        #
        #client_socket.sendto(TERMINATE, (server_name, server_port))
        #client_socket.recvfrom(len(TERMINATE))

        # print("CLIENT - Data to be sent to Server: {}".format(message))
        # client_socket.sendto(message, (server_name, server_port))       #send the message to the server
#
        # received_message, server_address = client_socket.recvfrom(200000)    # receive what the server sends back
        # print("CLIENT - Data received from Server: {}".format(received_message))

        client_socket.close()