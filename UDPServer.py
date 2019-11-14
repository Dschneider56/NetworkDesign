import io
from PIL import Image
from packet_functions import *
from threading import Thread


class UDPServer:
    def __init__(self):
        """
        receives data from the client, and creates a new image file that is a grayscale copy of the original
        """
        self.server_port = 12000  # server port number
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))  # bind the socket to an address

        logging.debug("SERVER - Server ready to receive.")

        self.listen_for_data = Thread(target=self.listen)     # Listen for data indefinitely on separate thread.
        self.listen_for_data.start()

    def listen(self):
        while True:
            # Receive packets from the client
            packets, client_address = receive_packets(self.server_socket)
            logging.debug('SERVER - All packets have been received')

            # Join the packets to a bytes object
            image = b''.join(packets)
            self.save_image(image)
            # Open the image to confirm the server could modify the original
            show_image = Image.open(io.BytesIO(image))
            show_image.show()

    def save_image(self, image: bytes):
        # Save the file to be retransmitted to sender
        saved_image = Image.open(io.BytesIO(image))
        logging.debug('SERVER - Image received and can be opened')

        # Save new file so we can read and create new packets to send back to the client
        saved_image.save('final-image.bmp', 'bmp')

    def __del__(self):
        """
        Destructor (currently a stub).

        :return:    None
        """
        self.listen_for_data.join()   # Stop the listening thread
        pass


if __name__ == '__main__':
    UDPServer()
