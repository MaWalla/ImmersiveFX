import serial
import numpy as np

from .device import Device


__all__ = [
    'Serial',
]


class Serial(Device):

    def __init__(self, device, *args, **kwargs):
        super().__init__(device, *args, **kwargs)

        path = device.get('path')

        try:
            self.serial_device = serial.Serial(path, device.get('baud'))
        except serial.serialutil.SerialException:
            print(f'WARNING: Serial device path "{path}" invalid. Disabling it.')
            self.enabled = False

    def set_serial_strip(self, data):
        """
        Sends an array of colors to a Serial device
        :param data: the color value in rgb
        """
        byte_data = bytes(np.array(data).ravel().tolist())
        self.serial_device.write(byte_data)

    def loop(self, data):
        self.set_serial_strip(data)
