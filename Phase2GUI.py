import io
from tkinter import *
from UDPServer import UDPServer
from UDPClient import UDPClient
from PIL import Image
from packet_functions import make_packet, send_packets, receive_packets


class ServerFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.server = UDPServer()


class ClientFrame(Frame):  # Inherits from class Frame
    def __init__(self, parent):
        self.client = UDPClient()

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
            p = make_packet(self.client.open_image(file_name))
            # Define the address of the server
            a = self.client.addr_and_port
            # Define the address of the client
            s = self.client.client_socket
            # Send the packets to the server
            send_packets(s, p, a)
            # Await response from the server
            packets, server_address = receive_packets(self.client.client_socket)

            # Join the packets back to a bytes object
            print('CLIENT - All packets have been received from the server')
            data = b''.join(packets)
            # Open the grayscale image to confirm the server could modify the original
            image = Image.open(io.BytesIO(data))
            print('CLIENT - Packets have been converted back to an image')
            image.show()

            # Close the client
            # self.client.client_socket.close()

        b = Button(root, text='Send File', command=send_image)
        b.pack(side='bottom')
        root.mainloop()


class App(Tk):
    def __init__(self):
        super().__init__()
        ServerFrame(self).pack(side='right')
        ClientFrame(self).pack(side='left')


if __name__ == '__main__':
    App()
