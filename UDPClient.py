import socket
from packet_functions import *
from PIL import Image   # PIL is used for image support in this program.
import io


class UDPClient:
    def __init__(self):
        """
        Send an image to server, then request a modified image back from the server.
        """
        server_address = '127.0.0.1'  # server address; it is the local host in this case
        server_port = 12000  # server port number
        client_socket = socket(AF_INET, SOCK_DGRAM)

        # Open and show the original image
        with open('island.bmp', 'rb') as image:  # open the file to be transmitted
            message = image.read()
            img = Image.open(io.BytesIO(message))
            img.show()

        # Convert the image to packets
        print("CLIENT - Creating packets")
        packets = make_packet(message)

        # Send the packets to the server
        print("CLIENT - Sending packets:")
        send_packets(client_socket, packets, (server_address, server_port))
        print("CLIENT - Finished sending packets")

        # Await for packets coming back from the server
        packets, server_address = receive_packets(client_socket)

        # Join the packets back to a bytes object
        print('CLIENT - All packets have been received from the server')
        data = b''.join(packets)
        # Open the grayscale image to confirm the server could modify the original
        image = Image.open(io.BytesIO(data))
        print('CLIENT - Packets have been converted back to an image')
        image.show()

        # Close the client
        client_socket.close()


if __name__ == '__main__':
    UDPClient()
