from UDPClient import UDPClient
from UDPServer import UDPServer


if __name__ == '__main__':
    UDPServer()  # Create server thread
    UDPClient()  # Create client object
