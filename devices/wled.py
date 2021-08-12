import socket

from .device import Device


__all__ = [
    'WLED',
]


class WLED(Device):
    
    def __init__(self, device, *args, **kwargs):
        super().__init__(device, *args, **kwargs)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = device.get('ip')
        self.port = device.get('port')

    def set_wled_strip(self, data):
        byte_data = bytes([2, 5, *data.ravel().astype(int).tolist()])

        self.sock.sendto(byte_data, (self.ip, self.port))

    def loop(self, data):
        self.set_wled_strip(data)
