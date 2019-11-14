from UDPClient import UDPClient
from UDPServer import UDPServer
import numpy as np
from packet_functions import *
import matplotlib.pyplot as plt

TRIALS = 10
TO_PERCENT = 0.65

if __name__ == '__main__':
    UDPServer()
    UDPClient()

