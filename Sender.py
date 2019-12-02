import socket
from packet_functions import *
import datetime as dt


class Sender:
    def __init__(self, file_name='island.bmp', timer_timeout=0.05, data_percent_loss=0, ack_percent_loss=0):
        """
        Send an image to receiver, then request a modified image back from the receiver.
        """
        self.message = b''
        receiver_address = '127.0.0.1'    # receiver address; it is the local host in this case
        receiver_port = 12000             # receiver port number
        self.addr_and_port = (receiver_address, receiver_port)
        self.sender_socket = socket(AF_INET, SOCK_DGRAM)
        self.file_name = file_name
        self.timeout = timer_timeout
        self.data_percent_loss = data_percent_loss
        self.ack_percent_loss = ack_percent_loss

        # Open the original image
        with open(file_name, 'rb') as image:  # open the file to be transmitted
            self.message = image.read()

        # Convert the image to packets
        logging.debug("sender - Creating packets")
        self.packets = make_packet(self.message)

        # Send the packets to the receiver
        logging.debug("sender - Sending packets:")

        # Record the time it takes to send the packets
        start_time = dt.datetime.now().timestamp()
        send_packets(self.sender_socket, self.packets, self.addr_and_port, data_percent_loss=self.data_percent_loss,
                     ack_percent_loss=self.ack_percent_loss, timer_timeout=self.timeout)
        end_time = dt.datetime.now().timestamp()
        self.delta_time = end_time - start_time
        logging.debug("sender - Finished sending packets")

        # Close the sender
        self.sender_socket.close()
        logging.debug(f'total time: {end_time - start_time}')

    def __del__(self):
        """
        Destructor

        :return:    None
        """


if __name__ == '__main__':
    Sender()
