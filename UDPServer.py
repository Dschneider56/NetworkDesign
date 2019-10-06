import io
from PIL import Image, ImageFile
from packet_functions import *


class UDPServer:
    def __init__(self):
        """
        receives data from the client, and creates a new image file that is a grayscale copy of the original
        """
        server_port = 12000  # server port number
        server_socket = socket(AF_INET, SOCK_DGRAM)
        data = []
        try:
            server_socket.bind(('', server_port))  # bind the socket to an address
        except Exception as e:
            print("SERVER - Server failed to initialize: {}".format(e))
            exit(0)

        print("SERVER - Server ready to receive.")
        while True:
            # Receive packets from the client
            packets, client_address = receive_packets(server_socket)
            print('SERVER - All packets have been received')

            # Join the packets to a bytes object
            image = b''.join(packets)

            # Convert the file to grayscale
            gray_image = Image.open(io.BytesIO(image))
            print('SERVER - Image received and can be opened')
            print('SERVER - Converting image to grayscale')
            gray_image = gray_image.convert('L')

            # Save new file so we can read and create new packets to send back to the client
            gray_image.save('sample-gray.bmp', 'bmp')
            with open('sample-gray.bmp', "rb") as showImage:
                read_img = showImage.read()

                # Create packets to send to the client
                print("SERVER - Creating packets")
                packets = make_packet(read_img)

                print("SERVER - Sending packets")
                # Send new packets to the client
                send_packets(server_socket, packets, client_address)
                print("SERVER - Finished sending packets")


if __name__ == '__main__':
    UDPServer()
