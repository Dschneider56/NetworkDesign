import socket
from packet_functions import *
from PIL import Image   # PIL is used for image support in this program.
import io
import datetime as dt


class UDPClient:
    def __init__(self, data_percent_corrupt=0, ack_percent_corrupt=0):
        """
        Send an image to server, then request a modified image back from the server.
        """
        self.message = b''
        self.data_percent_corrupt_ = data_percent_corrupt
        self.ack_percent_corrupt_ = ack_percent_corrupt
        server_address = '127.0.0.1'    # server address; it is the local host in this case
        server_port = 12000             # server port number
        self.addr_and_port = (server_address, server_port)
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.file_name = 'island.bmp'
        # Open and show the original image

        self.open_image(self.file_name)
        # Convert the image to packets
        logging.debug("CLIENT - Creating packets")
        self.packets = make_packet(self.message)

        # Send the packets to the server
        logging.debug("CLIENT - Sending packets:")

        # Record the time between initial send with some corruption percentage
        start_time = dt.datetime.now().timestamp()
        send_packets(self.client_socket, self.packets, self.addr_and_port, data_percent_corrupt=data_percent_corrupt)
        end_time = dt.datetime.now().timestamp()
        self.delta_time = end_time - start_time
        logging.debug("CLIENT - Finished sending packets")

        # Close the client
        self.client_socket.close()
        logging.debug(f'total time: {end_time - start_time}')

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
