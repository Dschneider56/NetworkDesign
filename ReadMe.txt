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

Sender.py 		- Contains class "Sender.py"; this class opens an image file (island.bp by default) and displays it.
			It then reads it as a binary and breaks it up into packets. An initializer statement is sent to the receiver
			which contains the number of packets the receiver should expect. These packets are sent to the receiver one
			at a time. Finally, it receives whatever packets the receiver sends back, reassembles the packets into a byte array, and displays
		 	this byte array as an image.


Receiver.py		- Contains class "UDPreceiver.py"; this class receives the packets sent to it by the sender until it receives a terminator sequence,
			then reassembles them into a byte array, converts this byte array into a grayscale image, and shows it. 
			Finally, it reads this grayscale image into a byte array, breaks it up into packets, and sends them back to the receiver.


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
    Go to line 101 of pack_functions.py and uncomment it. Then change the second parameter of the method to the
    percentage of error you would like to test for. This will give us a chance to change the ack to an invalid value
    and force the sender to resend the data. After that, run test.pty.

    - To test the file with data(checksum) corruption:
    Go to line 136 of pack_functions.py and uncomment it. Then change the second parameter of the method to the
    percentage of error you would like to test for. This will give us a chance to change the checksum to an invalid
    value and force the sender to resend the data. After that, run test.pty.


DEPENDENCIES:
	Pillow - an image processing library in Python.
	
