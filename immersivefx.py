import sys
import threading
from time import sleep, time

import numpy as np

from devices import WLED, Serial, DualShock


class Core:
    name = 'ImmersiveFX Core'  # override this in your fxmode

    # those need to be set by their respective fxmodes, as a list containing all applying values
    target_versions = None  # 'dev' works best for builtin fxmodes, external stuff should name actual versions though
    target_platforms = None  # check https://docs.python.org/3/library/sys.html#sys.platform or use 'all' if it applies

    def __init__(self, core_version, config, launch_arguments, *args, **kwargs):
        """
        fancy little base class, make your fxmode inherit from it to spare yourself unnecessary work
        or don't, I'm a comment not a cop.
        """
        self.launch_arguments = launch_arguments
        self.check_target(core_version)

        self.config = config
        self.devices = {}

        self.parse_devices(config)

        self.data_thread = None

        self.device_classes = {
            'wled': WLED,
            'serial': Serial,
            'dualshock': DualShock,

        }

        self.raw_data = np.zeros([1, 3])  # empty, but valid staring point
        self.frame_sleep = 1000 / self.config.get('fps', 30)

        self.splash()

    def start_threads(self):
        """
        initializes and starts data and device threads, call this in your fxmode, usually at the end
        """
        self.data_thread = threading.Thread(
            target=self.data_loop,
            args=(),
            kwargs={},
        )

        self.data_thread.start()
        self.start_device_threads()

    def start_device_threads(self):
        for device, device_config in self.devices.items():
            thread = device_config.get('thread')
            if thread:
                if not thread.ident:
                    thread.start()

    def parse_devices(self, config):
        """
        reads config.json and configures everything according to it. This method only takes care of the basics,
        so you may wanna extend it if your fxmode takes/requires additional settings.
        See fxmodes/screenfx/main.py for a reference implementation
        :return:
        """
        #  These keys need to be set per device, everything else has some kinda default instead
        required_keys = {
            'wled': {'ip', 'leds'},
            'serial': {'path', 'leds'},
            'dualshock': {'device_num'},
        }

        # Here we'll put the final configurations
        final_devices = {}

        devices = config.get('devices')

        if not devices:
            print('You didn\'t define devices in your config, which renders this program kinda useless')
            exit()

        for name, device in devices.items():
            device_enabled = device.get('enabled', True)

            if device_enabled:
                device_type = device.get('type')

                if device_type:
                    if device_type not in required_keys.keys():
                        print(f'WARNING: device {name} has an invalid type, must be {required_keys.keys()}, skipping it')
                    else:
                        if not (required_keys.get(device_type) - device.keys()):

                            base_config = {
                                'type': device_type,
                                'enabled': device_enabled,
                                'brightness': device.get('brightness', 1),
                                'flip': device.get('flip', False),
                                'color_temperature': device.get('color_temperature'),
                                'saturation': device.get('saturation', 1),
                                'thread': threading.Thread(),
                            }

                            if device_type == 'wled':
                                device_config = {
                                    'ip': device.get('ip'),
                                    'port': device.get('port', 21324),
                                    'leds': device.get('leds'),
                                    **base_config,
                                }
                            if device_type == 'serial':
                                baud = device.get('baud', 115200)

                                device_config = {
                                    'path': device.get('path'),
                                    'baud': baud,
                                    'leds': device.get('leds'),
                                    **base_config,
                                }

                            if device_type == 'dualshock':
                                device_config = {
                                    'device_num': device.get('device_num'),
                                    **base_config,
                                }

                            device_config['thread'] = threading.Thread(
                                target=self.device_loop,
                                args=[name],
                                kwargs={},
                            )

                            final_devices[name] = device_config

                        else:
                            print(f'WARNING: device {name} lacks one of these keys: '
                                  f'{required_keys.get(device_type)} skipping it.')
                else:
                    print(f'WARNING: you didn\'t define the device type for "{name}", skipping it.')

        if not final_devices:
            print('ERROR: There\'s no device with complete configuration, please check your config!')
            print('Exiting now...')
            exit(1)

        self.devices = final_devices

    def check_target(self, core_version):
        """
        checks if the user's ImmersiveFX Core version and platform match the fxmode requirements
        can be overridden with --no-version-check and --no-platform-check, expect errors in this case though
        """
        if not self.launch_arguments.no_version_check:
            match = None

            core_major, core_minor, *_ = core_version.split('.')
            for version in self.target_versions:
                major, minor, *_ = version.split('.')

                if (major, minor) == (core_major, core_minor):
                    match = True

            if not match:
                print('Your ImmersiveFX Core is on version %(core)s but it needs to be on %(targets)s' % {
                    'core': '.'.join([core_major, core_minor]),
                    'targets': ', '.join(self.target_versions),
                })
                print('for this FXMode to work!')
                exit(1)

        if not self.launch_arguments.no_platform_check:
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

    def data_processing(self, *args, **kwargs):
        """
        Override this in your fxmode and continuously set self.raw_data
        """
        pass

    def data_loop(self, *args, **kwargs):
        """
        Manages data cycle timing, for handling preferably use data_processing
        """
        while True:
            start = time()

            self.data_processing()

            duration = (time() - start) * 1000

            if duration > self.frame_sleep:
                if not self.launch_arguments.no_performance_warnings:
                    print('WARNING: data cycle took longer than frame time!')
                    print(f'frame time: {round(self.frame_sleep, 2)}ms, cycle time: {round(duration, 2)}ms')
                    print('If this happens repeatedly, consider lowering the fps.')
            else:
                sleep((self.frame_sleep - duration) / 1000)

    def device_processing(self, device, device_instance):
        """
        Override this in your fxmode and process raw data so you end up with a list of rgb arrays

        :param device: device info as per config, provided so that custom fxmode config keys can be respected
        :param device_instance: device class instance, containing further info
        :return: a 2d numpy array; a list of rgb lists
        """
        return np.zeros([1, 3])

    def device_loop(self, device_name):
        """
        Thread manager for a device. Creates a class instance for it and runs a continuous loop to send data

        :param device_name: key to fetch device_config
        """
        device = self.devices.get(device_name)
        device_type = device.get('type')
        device_class = self.device_classes.get(device_type)

        if device_class:
            device_instance = device_class(device, device_name)

            while True:
                if not device_instance.enabled:
                    break

                start = time()

                data = np.array(self.device_processing(device, device_instance))

                data = (device_instance.apply_enhancements(
                    data * device_instance.brightness * device_instance.color_temperature
                )).astype(int)

                if device_instance.flip:
                    data = np.flip(data, axis=0)

                device_instance.loop(data)

                duration = (time() - start) * 1000

                if duration > self.frame_sleep:
                    if not self.launch_arguments.no_performance_warnings:
                        print(f'WARNING: device "{device_instance.name}" cycle took longer than frame time!')
                        print(f'frame time: {round(self.frame_sleep, 2)}ms, cycle time: {round(duration, 2)}ms')
                        print('If this happens repeatedly, consider lowering the fps.')
                else:
                    sleep((self.frame_sleep - duration) / 1000)
