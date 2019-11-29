import io
from PIL import Image
from packet_functions import *
from threading import Thread


class Receiver:
    def __init__(self, data_percent_corrupt=0, ack_percent_corrupt=0):
        """
        receives data from the sender, and creates a new image file that is a grayscale copy of the original
        """
        self.ack_percent_corrupt = ack_percent_corrupt
        self.data_percent_corrupt = data_percent_corrupt
        self.receiver_port = 12000  # receiver port number
        self.receiver_socket = socket(AF_INET, SOCK_DGRAM)
        self.receiver_socket.bind(('', self.receiver_port))  # bind the socket to an address

        logging.debug("receiver - receiver ready to receive.")

        self.listen_for_data = Thread(target=self.listen)     # Listen for data indefinitely on separate thread.
        self.listen_for_data.start()

    def listen(self):
        # Receive packets from the sender
        packets, sender_address = receive_packets(self.receiver_socket,
                                                  data_percent_corrupt=self.data_percent_corrupt,
                                                  ack_percent_corrupt=self.ack_percent_corrupt)
        logging.debug('receiver - All packets have been received')

        # Join the packets to a bytes object
        image = b''.join(packets[1:])
        self.save_image(image)
        # Open the image to confirm the receiver could modify the original
        show_image = Image.open(io.BytesIO(image))
        show_image.show()

    def save_image(self, image: bytes):
        # Save the file to be retransmitted to sender
        saved_image = Image.open(io.BytesIO(image))
        logging.debug('receiver - Image received and can be opened')

        # Save new file so we can read and create new packets to send back to the sender
        saved_image.save('final-image.bmp', 'bmp')

    def __del__(self):
        """
        Destructor (currently a stub).

        :return:    None
        """
        pass


if __name__ == '__main__':
    Receiver()
