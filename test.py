from UDPClient import Client
from UDPServer import Server
from threading import Thread

if __name__ == '__main__':
    Thread(target=Server).start()   # Create server thread
    Client()    # Create client object