Author: Dylan Schneider

Files submitted: UDPClient.py, UDPServer.py, sample.png

***File Descriptions***

UDPClient.py creates a client socket, and takes user input for the file name to be transferred. This file will display
the original image, and then encode it in base64 so it may be passed on to the server. After sending the file to the
server, the client waits for a response. Once it receives a response,the client will decode and display the new image.

UDPServer.py initializes a server and waits for incoming data. Upon receiving data from the client, the server
decodes the image and then converts it to grayscale.

The server then saves the grayscale image as a new file, so it may be read and encoded for transfer back to the client
(This workflow may be replaced in later stages if better methods are discovered as I would prefer not to make an entire
new file on the server).

The server then sends the new image to the client, and continues to wait for more data.

sample.png is a small colorful image file that I used for testing file transfer. Currently the size of images to be
transferred is very small, as using larger files causes runtime errors. The intent is that large data transfer will be
supported upon completion of phase 2.

***Steps to run the program***
Both the client and server need to run simultaneously for this code to run without error. The server is set to run on
localhost:12000 on the machine running the code, so if a process is already running on that port, than the serverPort
variables in the client and server should be changed to a free port. Other than that, no configuration needs to be
done prior to running UDPServer.py and UDPClient.py.

After running the code, the client will prompt the user for the name of the file they would like to transfer. The user
should enter the name of a very small (less than 8kb) image file. This code contains 'sample.png' which fits the
criteria and will not need a path specified to be used, but if the user wishes to test with their own file they may need
to specify the path as well.

After specifying the file, the rest of the code runs without any work required from the user. The program will display
both the grayscale version of the image, and the original image to the user. Since the server is the part of the code
that modifies the image, seeing the grayscale image confirms that the server handled and returned the image back
to the client.
