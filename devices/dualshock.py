import glob

from .device import Device


__all__ = [
    'DualShock',
]


class DualShock(Device):
    ds4_paths = {
        counter + 1: path
        for counter, path in enumerate(glob.glob('/sys/class/leds/0005:054C:05C4.*:global'))
    }

    def __init__(self, device, *args, **kwargs):
        super().__init__(device, *args, **kwargs)

        device_num = device.get('device_num')
        self.path = self.ds4_paths.get(device_num)

        if not self.path:
            print(f'WARNING: DualShock Controller with device_num {device_num} specified,')
            print(f'but there is no device path available for it. Disabling it.')
            self.enabled = False

    def set_dualshock_color(self, color):
        """
        Sends an rgb color to a DualShock 4 controller for its lightbar
        :param color: rgb value that is sent to the lightbar
        """
        red, green, blue = color

        # TODO improve the path handling. [:-6 ain't the best solution]
        red_path = f'{self.path[:-6]}red/brightness'
        green_path = f'{self.path[:-6]}green/brightness'
        blue_path = f'{self.path[:-6]}blue/brightness'

        r = open(red_path, 'w')
        r.write(str(red))
        r.close()

        g = open(green_path, 'w')
        g.write(str(green))
        g.close()

        b = open(blue_path, 'w')
        b.write(str(blue))
        b.close()

    def loop(self, data):
        """
        Function that will be repeatedly called by a threadloop.

        :param data: 2d array containing a list of rgb values for the target device
        """

        # we get a list of rgb values which only contains one entry (since there is only one LED), so we grab that
        self.set_dualshock_color(data[0])
