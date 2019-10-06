from tkinter import *
from UDPServer import UDPServer
from UDPClient import UDPClient
from packet_functions import make_packet, send_packets, receive_packets


class ClientFrame(Frame):  # Inherits from class Frame
    def __init__(self, parent):
        super().__init__(parent)
        self.client = UDPClient()
        Label(text='Client Side').pack()

        canvas = Canvas(parent, )
        Button(parent, text='Send Image',
               command=lambda s=self.client.client_socket,
                              p=self.client.packets,
                              a=self.client.addr_and_port:
               send_packets(s, p, a)).pack(side='top')

    def show_img(self):



class ServerFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.server = UDPServer()


class App(Tk):
    def __init__(self):
        super().__init__()
        ServerFrame(self).pack(side='right')
        ClientFrame(self).pack(side='left')
        self.mainloop()


if __name__ == '__main__':
    App()
