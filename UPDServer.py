from socket import *
from PIL import Image
import io
import base64
# Create server socket
serverPort = 12000
# AF_INET specifies an IPv4, SOCK_DGRAM specifies UDP connection (not TCP)
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Set server port to 12000
serverSocket.bind(('', serverPort))
print("The server is ready to receive")
# Check if message came from client, if so, make message upper case and send back to client
while True:
    # Store contents in message variable. Store client information in clientAddress variable
    image, clientAddress = serverSocket.recvfrom(8192)
    # Decode file
    clientImage = base64.decodebytes(image)
    # Convert the file to grayscale
    newImage = Image.open(io.BytesIO(clientImage)).convert('L')
    # Save new file so we can encode it and send it back to the client
    newImage.save('sample-gray', 'png')
    with open('sample-gray', "rb") as image:
        # Open the original image
        read_img = image.read()

    # Encode new image file
    image_64_encode = base64.encodebytes(read_img)

    # Send modified image back to client
    serverSocket.sendto(image_64_encode, clientAddress)
