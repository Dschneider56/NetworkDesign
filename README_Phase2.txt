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

UDPClient.py 		- Contains class "UDPClient.py"; this class opens an image file (island.bp by default) and displays it. 
			It then reads it as a binary and breaks it up into packets. These packets are sent to the 
			server one at a time, and sends a terminating character sequence once all the packets have been sent. Finally, 
			it receives whatever packets the server sends back, reassembles the packets into a byte array, and displays
		 	this byte array as an image.


UDPServer.py		- Contains class "UDPServer.py"; this class receives the packets sent to it by the client until it receives a terminator sequence,
			then reassembles them into a byte array, converts this byte array into a grayscale image, and shows it. 
			Finally, it reads this grayscale image into a byte array, breaks it up into packets, and sends them back to the server.


packet_functions.py	- Contains the functions "make_packet", "send_packets", and "receive_packets". Classes UDPClient and UDPServer call send_packet
			and receive_packet to send and receive packets respectively. 

			- "make_packet" splits up a byte array into packets 2 kb in size and returns them as a list of byte arrays.

			- "send_packets" takes a list of byte arrays and sends them through a socket one at a time. When the last packet is sent, a
			terminator character sequence is sent to signal that the complete message has been sent.

			- "receive_packets" continuously receives the packets being sent until it receives a terminator sequence. It then returns a list
			of byte arrays representing each packet.

			- "short_sleep" is a very short delay thats called between sending packets in send_packets. This prevents data loss.


test.py			- This is the main executable; Run this script to initiate the Client -> Server -> Client communication process.


INSTRUCTIONS:

	- Run the file "test.py". UDPClient will display the original image (island.bmp) and send it to UDPServer. Then, UDPServer will convert that image to grayscale,
	show it, then send that grayscale image back to UDPClient. Finally, UDPClient will display the image it received from UDPServer, which is a 
	grayscale version of the original image.
	
	**NOTE: This program will create 2 .bmp grayscale images.

DEPENDENCIES:
	Pillow - an image processing library in Python.
	
