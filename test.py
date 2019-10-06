from UDPClient import UDPClient
from UDPServer import UDPServer
from threading import Thread


if __name__ == '__main__':
    Thread(target=UDPServer).start()   # Create server thread
    UDPClient()    # Create client object