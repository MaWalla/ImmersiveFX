import numpy as np
from math import sqrt

__all__ = [
    'Device',
]


class Device:
    """
    Generic class for devices
    """

    def __init__(self, device, *args, **kwargs):
        """
        common attributes
        """
        self.name = device.get('name')
        self.enabled = device.get('enabled')

        self.brightness = device.get('brightness')
        self.flip = device.get('flip')
        self.color_correction = device.get('color_correction')
        self.leds = device.get('leds', 1)

    def process_data(self, data):
        """
        converts a list of rgb values into something device-compatible
        :param data: a list of rgb values
        """

        if self.flip:
            data = np.flip(data, axis=0)

        flat_data = np.array([
            self.color_correction(np.array(value) * self.brightness)
            for value in data
        ]).astype(int).ravel()

        if self.color_correction:
            flat_data = self.color_correction(flat_data)

        return flat_data

    def loop(self, data):
        """
        Function that will be repeatedly called by a threadloop.
        It should do the necessary work to get the device to display the sent data.

        :param data: 2d array containing a list of rgb values for the target device
        """

    def __str__(self):
        return self.name
