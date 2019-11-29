import io
from tkinter import *
from Receiver import Receiver
from Sender import Sender
from PIL import Image
from packet_functions import make_packet, send_packets, receive_packets


class receiverFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.receiver = Receiver()


class senderFrame(Frame):  # Inherits from class Frame
    def __init__(self, parent):
        self.sender = Sender()

        root = Tk()
        global e
        e = Entry(root)
        e.pack()
        e.focus_set()

        root.title('Enter file name (path required if not in project directory)')

        def send_image():
            # Get the file name from the user
            file_name = e.get()
            # Break down the file to packets
            p = make_packet(self.sender.open_image(file_name))
            # Define the address of the receiver
            a = self.sender.addr_and_port
            # Define the address of the sender
            s = self.sender.sender_socket
            # Send the packets to the receiver
            send_packets(s, p, a)
            # Await response from the receiver
            packets, receiver_address = receive_packets(self.sender.sender_socket)

            # Join the packets back to a bytes object
            print('sender - All packets have been received from the receiver')
            data = b''.join(packets)
            # Open the grayscale image to confirm the receiver could modify the original
            image = Image.open(io.BytesIO(data))
            print('sender - Packets have been converted back to an image')
            image.show()

            # Close the sender
            # self.sender.sender_socket.close()

        b = Button(root, text='Send File', command=send_image)
        b.pack(side='bottom')
        root.mainloop()


class App(Tk):
    def __init__(self):
        super().__init__()
        receiverFrame(self).pack(side='right')
        senderFrame(self).pack(side='left')


if __name__ == '__main__':
    App()
