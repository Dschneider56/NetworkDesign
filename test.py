from Sender import Sender
from Receiver import Receiver


if __name__ == '__main__':
    Receiver(data_percent_corrupt=0, ack_percent_corrupt=0)
    Sender(timer_timeout=0.05, data_percent_loss=0, ack_percent_loss=0)
