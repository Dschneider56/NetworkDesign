TITLE:	Phase 2


AUTHORS:
	- Roarke Myers
	- Dylan Schneider
	- Josias Polonia


ENVIRONMENT:
	- Written using Python 3.7.5
	- Compatible with Windows 10, Mac OS
	- Developed and tested using Pycharm Community Edition IDE


FILES:

Sender.py 		- Contains class "Sender.py"; this class opens an image file (island.bmp by default).
			It then reads it as a binary and breaks it up into packets. An initializer statement is sent to the receiver
			which contains the number of packets the receiver should expect. These packets are sent to the receiver one
			at a time. Between each packet it waits for the receiver to send an acknowledgement confirming the packet
			was received properly. The sender then continues sending packets until all are sent. Lastly it sends a
			terminate statement to the receiver so both the sender and receiver know to stop listening.

			The sender has optional parameters in the constructor so the user may test data/ack loss. By inputting a
			probability between 0 and 1 the user can chose what percentage of data to drop and observe how it affects
			performance time. Default is no corruption.


Receiver.py		- Contains class "Receiver.py"; this class receives the packets sent to it by the sender until it
            receives a terminator sequence, then reassembles them into a byte array, converts this byte array into an
            image, and shows it. Finally, it displays the image it received.

            The receiver has optional parameters in the constructor so the user may test data/ack corruption. By
            inputting a probability between 0 and 1 the user can chose what percentage of data to corrupt and observe
            how it affects performance time. Default is no corruption.


packet_functions.py	- Contains the functions "make_packet", "send_packets", "receive_packets", "parse_packets",
"corrupt_checksum", and "corrupt_ack". Classes Sender and Receiver call send_packet
			and receive_packet to send and receive packets respectively. 

			- "make_packet" splits up a byte array into packets 2 kb in size and returns them as a list of byte arrays.

			- "send_packets" takes a list of byte arrays and sends them through a socket one at a time. When the last packet is sent, a
			terminator character sequence is sent to signal that the complete message has been sent.

			- "receive_packets" continuously receives the packets being sent until it all expected packets are received.
			 It then returns a list of byte arrays representing each packet.

			- "parse_packets" parses the sequence number, checksum, and data from the packet

			- "corrupt_ack" has a random chance (odds determined by the user) to corrupt the received ack

			- "corrupt_checksum" has a random chance (odds determined by the user) to corrupt the received checksum


test.py			- This is the main executable; Run this script to initiate the sender -> receiver -> sender communication process.


INSTRUCTIONS:

	- To Test the file with no corruption:
	Run the file "test.py". Sender will send the original image (island.bmp) to Receiver. Then, Receiver will save the image and
	then send the image back to Sender. Finally, Sender will display the image it received from Receiver,
	this should be identical to the original image
	
	**NOTE: This program will create a new .bmp image.

    - To test the file with ack corruption:
    In the receiver constructor add the parameter ack_percent_corrupt and set it equal to a probability between 0 and 1

    - To test the file with data(checksum) corruption:
    In the receiver constructor add the parameter data_percent_corrupt and set it equal to a probability between 0 and 1

    - To test the file with ack loss:
    In the sender constructor add the parameter ack_percent_loss and set it equal to a probability between 0 and 1

    - To test the file with data(checksum) loss:
    In the receiver constructor add the parameter data_percent_loss and set it equal to a probability between 0 and 1


DEPENDENCIES:
	Pillow - an image processing library in Python.
	
