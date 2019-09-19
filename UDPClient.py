from socket import *
# PIL is used for image support in this program.
from PIL import Image
import base64
import io

# Set server to localhost:12000
serverName = 'localhost'
serverPort = 12000
# Create client socket
# AF_INET specifies an IPv4, SOCK_DGRAM specifies UDP connection (not TCP)
clientSocket = socket(AF_INET, SOCK_DGRAM)
# Prompt user for input string to pass to server
fileName = input('Input file name:')
with open(fileName, "rb") as image:
    # Open the original image
    read_img = image.read()
    img = Image.open(io.BytesIO(read_img))
    img.show()

# Encode original image to send to server
image_64_encode = base64.encodebytes(read_img)

# Send file to the server
clientSocket.sendto(image_64_encode, (serverName, serverPort))

# Await response from server
serverImage, serverAddress = clientSocket.recvfrom(8192)

# display the greyscale image that came back from the server
modifiedImage = base64.decodebytes(serverImage)
display_image = Image.open(io.BytesIO(modifiedImage))
display_image.show()
# Close the client
clientSocket.close()

