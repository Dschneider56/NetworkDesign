import concurrent.futures
import socket
import time

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
        self.timer_timeout = timer_timeout
        self.timeout = False
        self.data_percent_loss = data_percent_loss
        self.ack_percent_loss = ack_percent_loss

        # Open the original image
        self.open_image(self.file_name)

        # Convert the image to packets
        logging.debug("sender - Creating packets")
        self.packets = make_packet(self.message)

        # Send the packets to the receiver
        logging.debug("sender - Sending packets:")

        # Record the time it takes to send the packets
        start_time = dt.datetime.now().timestamp()
        self.send_packets()
        end_time = dt.datetime.now().timestamp()
        self.delta_time = end_time - start_time
        logging.debug("sender - Finished sending packets")

        # Close the sender
        self.sender_socket.close()
        logging.debug(f'total time: {end_time - start_time}')

    def open_image(self, file_name):
        with open(file_name, 'rb') as image:  # open the file to be transmitted
            self.message = image.read()
            return self.message

    def run_timer(self):
        self.timeout = False
        start_time = time.time()
        end_time = start_time + self.timer_timeout
        while time.time() < end_time:
            if self.timeout is True:
                self.timeout = False
                return self.timeout
            sleep(0.002)

        # If timed out, return True
        logging.debug("TIMED OUT")
        self.timeout = True
        return self.timeout

    def send_packets(self):
        """
        Send a collection of packets to a destination address through a socket.
        :param sock:            socket used to send packets to the receiver
        :param packets:         The collection of packets.
        :param addr_and_port:   A tuple containing the destination address and destination port number
        :param data_percent_loss:    The probability that we should lose the data the sender gets from the receiver
        :param ack_percent_loss:    The probability that we should corrupt the ack the sender gets from the receiver

        :return:                None
        """

        logging.debug("Sending initialization statement:")

        # Create an initialize statement and append the number of packets the receiver should expect
        # len(packets) is the number of packets of data we send, and we add 1 for the initializer
        initializer = bytes(str(INITIALIZE) + str(len(self.packets) + 1), 'utf-8')
        logging.debug("INITIALIZER ----------------------")

        checksum = bytes(format(sum(initializer), '024b'), 'utf-8')  # Create a checksum for the initializer.

        # Initialize the sequence number
        seqnum = bytes(str(0), 'utf-8')

        initializer_packet = initializer + checksum + seqnum  # Combine seqnum, checksum, & initializer into a packet

        self.packets.insert(0, initializer_packet)  # Append the initializer to the start of our list of packets

        # i is the index of our packets list which we will use to send packets in the proper order.
        i = 0
        while i < len(self.packets):
            logging.debug("SEND_PACKETS: inside for loop for packet " + str(i + 1))
            ack = i % 2
            received_ack = -1
            received_checksum = -1

            received_data = self.send_packet_with_timeout(self.packets[i], self.addr_and_port)

            if received_data == TERMINATE:
                i = len(self.packets)
                continue
            if received_data is None:
                # Resend data if nothing comes back
                continue

            received_ack = int(received_data[:1])
            received_checksum = str(received_data[1:])

            logging.debug(f'SENDER: received data: {received_data}')

            # If instructed to corrupt data do so, otherwise do nothing these next 2 lines
            received_checksum = corrupt_checksum(received_checksum, self.data_percent_loss)
            received_ack = corrupt_ack(received_ack, self.ack_percent_loss)

            if (received_ack == ack) and (received_checksum == "b'111111111111111111111111'"):
                logging.debug("ACK and Checksum received for packet " + str(i + 1))
                i += 1
            elif received_ack != ack:
                logging.debug("invalid ack from packet " + str((i + 1)) + ", resending data")
                # If ack does not change resend that packet

            else:
                logging.debug("Invalid checksum received from packet " + str((i + 1)) + ", resending data")
                # If checksum is incorrect, subtract 1 from i and resend that packet
        logging.debug('COMPLETE\n')

    def send_packet_with_timeout(self, packet, addr_and_port: tuple):
        """
            Send an individual packet and run a timer on seperate threads
            When timer finishes set a flag to indicate a timeout and cancel the thread to receive response from receiver
            If we get a response from the receiver, stop the timer thread.

            :param sock:            The socket object through which the packets will be sent
            :param packets:         The collection of packets.
            :param addr_and_port:   A tuple containing the destination address and destination port number
            :param data_percent_loss:    The probability that we should lose the data the sender gets from the receiver
            :param ack_percent_loss:    The probability that we should corrupt the ack the sender gets from the receiver

            :return:                None
            """

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Set initial values
            received_data = None
            self.timeout = False
            data_size = CHECKSUM_SIZE + SEQNUM_SIZE

            logging.debug("ENTERED CONCURRENT STUFF")

            # Send the packet on to the receiver
            self.sender_socket.sendto(packet, addr_and_port)

            logging.debug("SENT PACKET TO SERVER")

            # Start a timer on its own thread
            timer = executor.submit(self.run_timer)

            logging.debug("STARTED TIMER")

            await_response = executor.submit(self.sender_socket.recvfrom, data_size)

            logging.debug("STARTED LISTENING FOR RESPONSE FROM RECEIVER")

            # wait for response from timer
            self.timeout = timer.result()
            logging.debug("hello")
            logging.debug(bool(timer.result))

            # Wait fo response from the receiver
            received_data, return_address = await_response.result()

        while True:
            if received_data is not None:
                logging.debug("RESPONSE FROM RECEIVER HAS BEEN RECEIVED")
                self.timeout = True
                return received_data
            if self.timeout:
                logging.debug("TIMER HAS REACHED TIMEOUT")
                # If we have timed out, cancel
                await_response.cancel()
                return received_data
            sleep(0.002)

    def __del__(self):
        """
        Destructor

        :return:    None
        """


if __name__ == '__main__':
    Sender()
