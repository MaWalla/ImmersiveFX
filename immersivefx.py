import glob
import socket
import sys
from math import sqrt

import numpy as np


class Core:
    name = 'ImmersiveFX Core'  # override this in your fxmode

    # those need to be set by their respective fxmodes, as a list containing all applying values
    target_versions = None  # 'dev' works best for builtin fxmodes, external stuff should name actual versions though
    target_platforms = None  # check https://docs.python.org/3/library/sys.html#sys.platform or use 'all' if it applies

    def __init__(self, devices, core_version, config, *args, flags=[], **kwargs):
        """
        fancy little base class, make your fxmode inherit from it to spare yourself unnecessary work
        or don't, I'm a comment not a cop.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ds4_paths = {
            counter + 1: path
            for counter, path in enumerate(glob.glob('/sys/class/leds/0005:054C:05C4.*:global'))
        }
        self.devices = devices

        self.config = config
        self.flags = flags
        self.check_target(core_version)
        self.splash()

    def loop(self):
        """
        This function will be continuously called by main.py
        So override it and let it do some magic!
        """
        pass

    def check_target(self, core_version):
        """
        checks if the user's ImmersiveFX Core version and platform match the fxmode requirements
        can be overridden with --no-version-check and --no-platform-check, expect errors in this case though
        """
        if '--no-version-check' not in self.flags:
            if core_version not in self.target_versions and 'dev' not in self.target_versions:
                print('your ImmersiveFX Core is on version %(core)s but it needs to be %(targets)s.' % {
                    'core': core_version,
                    'targets': ', '.join(self.target_versions),
                })
                exit()

        if '--no-platform-check' not in self.flags:
            if sys.platform not in self.target_platforms and 'all' not in self.target_platforms:
                print('your platform is %(platform)s but it needs to be %(targets)s.' % {
                    'platform': sys.platform,
                    'targets': ', '.join(self.target_platforms),
                })
                exit()

    def splash(self):
        """
        Override this in your fxmode and print whatever you want. Preferably some kinda logo of course
        """

        print('***************************************************')
        print('*           NO SPLASH SCREEN SPECIFIED!           *')
        print('*  you\'re seeing this because the fxmode creator  *')
        print('*      didn\'t override the splash() method.       *')
        print('*        No big deal but kinda boring, huh?       *')
        print('***************************************************')

    @staticmethod
    def color_correction(rgb):
        """
        Corrects an rgb value for (my) WS2811 strip. The given formular isn't too expensive but highly
        subjective towards my LEDs and personal feeling about somewhat accurate colors.
        :param rgb: input rgb list
        :return: corrected rgb list
        """
        rgb[1] = int((sqrt(rgb[1]) ** 1.825) + (rgb[1] / 100))
        rgb[2] = int((sqrt(rgb[2]) ** 1.775) + (rgb[2] / 100))
        return rgb

    def set_wled_color(self, wled, rgb):
        """
        Sends a single color to the whole WLED strip
        :param wled: The WLED device
        :param rgb: the color value in rgb
        """
        corrected_rgb = self.color_correction(rgb)
        byte_data = bytes([2, 5, *np.array([corrected_rgb for _ in range(wled['leds'])]).ravel()])
        self.sock.sendto(byte_data, (wled['ip'], wled['port']))

    def set_wled_strip(self, wled, data):
        """
        Sends an array of colors to a wled device
        :param wled: The WLED device
        :param rgb: the color value in rgb
        """
        byte_data = bytes([2, 5, *np.array(data).ravel().tolist()])
        self.sock.sendto(byte_data, (wled['ip'], wled['port']))

    @staticmethod
    def set_ds4_color(lightbar_color, path):
        """
        Sends an rgb color to a DualShock 4 controller for its lightbar
        :param lightbar_color: rgb value that is sent to the lightbar
        :param path: device path that's gonna be used
        """
        red, green, blue = lightbar_color

        red_path = f'{path[:-6]}red/brightness'
        green_path = f'{path[:-6]}green/brightness'
        blue_path = f'{path[:-6]}blue/brightness'

        r = open(red_path, 'w')
        r.write(str(red))
        r.close()

        g = open(green_path, 'w')
        g.write(str(green))
        g.close()

        b = open(blue_path, 'w')
        b.write(str(blue))
        b.close()
