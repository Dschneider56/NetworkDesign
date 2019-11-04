import socket
from packet_functions import *
from PIL import Image   # PIL is used for image support in this program.
import io


class UDPClient:
    def __init__(self):
        """
        Send an image to server, then request a modified image back from the server.
        """
        self.message = b''
        server_address = '127.0.0.1'    # server address; it is the local host in this case
        server_port = 12000             # server port number
        self.addr_and_port = (server_address, server_port)
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.file_name = 'island.bmp'
        # Open and show the original image

        self.open_image(self.file_name)
        # Convert the image to packets
        print("CLIENT - Creating packets")
        self.packets = make_packet(self.message)

        # Send the packets to the server
        print("CLIENT - Sending packets:")
        send_packets(self.client_socket, self.packets, self.addr_and_port)
        print("CLIENT - Finished sending packets")

        # Await for packets coming back from the server
        packets, server_address = receive_packets(self.client_socket)

        # Join the packets back to a bytes object
        print('CLIENT - All packets have been received from the server')
        data = b''.join(packets)
        # Open the grayscale image to confirm the server could modify the original
        image = Image.open(io.BytesIO(data))
        print('CLIENT - Packets have been converted back to an image')
        image.show()
        # Close the client
        self.client_socket.close()

    def open_image(self, file_name):
        with open(file_name, 'rb') as image:  # open the file to be transmitted
            self.message = image.read()
            return self.message

    def __del__(self):
        """
        Destructor

        :return:    None
        """
    #    del self.file_name
        del self.message


if __name__ == '__main__':
    UDPClient()
