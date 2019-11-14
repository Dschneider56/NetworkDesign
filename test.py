from UDPClient import UDPClient
from UDPServer import UDPServer


TRIALS = 10
TO_PERCENT = 0.65

if __name__ == '__main__':
    UDPServer()
    UDPClient(timeout=1, ack_percent_corrupt=.9)

