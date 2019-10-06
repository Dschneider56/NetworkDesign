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

        print("SERVER - Server ready to receive.")

        self.listen_for_data = Thread(target=self.listen)     # Listen for data indefinitely on separate thread.
        self.listen_for_data.start()

    def listen(self):
        while True:
            # Receive packets from the client
            packets, clientAddress = receive_packets(self.server_socket)
            print('SERVER - All packets have been received')

            # Join the packets to a bytes object
            image = b''.join(packets)
            self.create_grayscale_img(image)

            with open('sample-gray.bmp', "rb") as showImage:
                read_img = showImage.read()

                # Create packets to send to the client
                print("SERVER - Creating packets")
                packets = make_packet(read_img)

                # Send new packets to the client
                send_packets(self.server_socket, packets, clientAddress)

    def create_grayscale_img(self, image: bytes):
        # Convert the file to grayscale
        grayImage = Image.open(io.BytesIO(image))
        print('SERVER - Image received and can be opened; converting image to grayscale')
        grayImage = grayImage.convert('L')

        # Save new file so we can read and create new packets to send back to the client
        grayImage.save('sample-gray.bmp', 'bmp')

    def __del__(self):
        """
        Destructor (currently a stub).

        :return:    None
        """
        self.listen_for_data.join()   # Stop the listening thread
        pass


if __name__ == '__main__':
    UDPServer()
