import threading
import colorsys
import numpy as np

from immersivefx import Core
from .bands import Bands, calculate_octave_bands
from .pacmd import list_sources


class PulseViz(Core):
    name = 'PulseViz'

    target_versions = ['dev']
    target_platforms = ['linux']

    modes = ['intensity', 'rainbow road']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = self.get_mode()

        self.band_mapping = {
            0: [255, 0, 0],
            1: [255, 0, 0],
            2: [255, 0, 0],
            3: [255, 0, 0],
            4: [255, 0, 0],
            5: [255, 0, 0],
            6: [255, 0, 0],
            7: [255, 0, 0],
            8: [255, 0, 0],
            9: [255, 128, 0],
            10: [255, 255, 0],
            11: [255, 255, 0],
            12: [255, 255, 0],
            13: [255, 255, 0],
            14: [255, 255, 0],
            15: [128, 255, 0],
            16: [0, 255, 0],
            17: [0, 255, 0],
            18: [0, 255, 0],
            19: [0, 255, 0],
            20: [0, 255, 0],
            21: [0, 255, 128],
            22: [0, 255, 255],
            23: [0, 255, 255],
            24: [0, 255, 255],
            25: [0, 255, 255],
            26: [0, 255, 255],
            27: [0, 128, 255],
            28: [0, 0, 255],
            29: [0, 0, 255],
            30: [0, 0, 255],
            31: [0, 0, 255],
            32: [0, 0, 255],
            33: [0, 0, 255],
        }

        self.rainbow_offset = 0
        self.acceleration_weight = {
            0: 0.75,
            1: 0.75,
            2: 0.75,
            3: 0.75,
            4: 0.83,
            5: 0.83,
            6: 1,
            7: 1,
            8: 0.83,
            9: 0.83,
            10: 0.75,
            11: 0.5,
            12: 0.33,
            13: 0.33,
            14: 0.33,
            15: 0.33,
            16: 0.33,
            17: 0.33,
            18: 0.33,
            19: 0.33,
            20: 0.25,
            21: 0.25,
            22: 0.25,
            23: 0.25,
            24: 0.25,
            25: 0.2,
            26: 0.2,
            27: 0.2,
            28: 0.15,
            29: 0.15,
            30: 0.15,
            31: 0.1,
            32: 0.1,
            33: 0.1,
        }

        bands_data = {
            'source_name': self.get_source_name(),
            'sample_frequency': 44100,
            'sample_size': 8192,
            'window_size': 1024,
            'window_overlap': 0.5,
            'window_function': 'hanning',
            'weighting': 'Z',
            'band_frequencies': calculate_octave_bands(fraction=3)
        }

        self.pulseviz_bands = Bands(**bands_data)
        self.start_bands()

    def splash(self):
        print('Welcome to ----------------------------- by MaWalla')
        print('        ███ █  █ █    ██ ███ █   █ ███ ████        ')
        print('        █ █ █  █ █   █   █   █   █  █     █        ')
        print('        ███ █  █ █    █  ██  ██ ██  █   ██         ')
        print('        █   █  █ █     █ █    ███   █  █           ')
        print('        █    ██  ███ ██  ███   █   ███ ████        ')
        print('-- backend: https://github.com/pckbls/pulseviz.py -')

    def get_mode(self):
        """
        Choice menu for the preferred way to display the acquired pulseaudio data,
        can also be set statically by setting a "pulseviz_mode" key in the config
        """
        selected_mode = self.config.get('pulseviz_mode')

        while selected_mode not in self.modes:
            print('---------------------------------------------------')
            print('No PulseViz visualisation was defined, pick one now:\n')
            for index, mode in enumerate(self.modes):
                print(f'{index}: {mode}')

            choice = input()

            try:
                selected_mode = self.modes[int(choice)]
            except (IndexError, ValueError):
                print('Invalid choice!')
                print(f'It must be a number bigger than 0 and smaller than {len(self.modes)}, try again!')

        return selected_mode

    def get_source_name(self):
        """
        Choice menu for the used pulseaudio source,
        can also be set statically by setting a "source_name" key in the config.
        Options can be manually obtained with pactl list sources | grep 'Name:'
        """
        sources = list_sources()
        chosen_source = self.config.get('source_name')
        while chosen_source not in sources:
            print('---------------------------------------------------')
            print('PulseViz requires an audio source but no source_name was defined ')
            print('or the source isn\'t available right now. Pick another source please:\n')
            for index, source in enumerate(sources):
                print(f'{index}: {source}')

            choice = input()

            try:
                chosen_source = sources[int(choice)]
            except (IndexError, ValueError):
                print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(sources)}, try again!')

        return chosen_source

    def start_bands(self):
        self.pulseviz_bands.start()

    def stop_bands(self):
        self.pulseviz_bands.stop()

    @staticmethod
    def data_conversion(value, minimum, maximum):
        multiplicator = (value - minimum) / (maximum - minimum)
        return multiplicator * multiplicator * multiplicator

    @staticmethod
    def post_process_color(value, color):
        if value != color.max():
            value *= 0.8

        value *= 255 / (color.max() or 1)

        return value

    def intensity_mode(self, values):
        converted_values = [[
            self.data_conversion(value, values.min(), values.max()) * color if not np.isinf(value) else 0
            for color in self.band_mapping[num]
        ] for num, value in enumerate(values)]

        color = np.array(converted_values).mean(axis=0)
        normalized_color = np.clip([
            self.post_process_color(rgb, color) for rgb in color
        ], 0, 255).astype(int).tolist()

        for device in self.devices:
            if device['enabled']:
                if device['type'] == 'esp':
                    ip = device['ip']
                    port = device['port']
                    brightness = device['brightness']
                    kelvin = device['kelvin']

                    threading.Thread(
                        target=self.set_esp_colors,
                        args=(),
                        kwargs={
                            'ip': ip,
                            'port': port,
                            'brightness': brightness,
                            'kelvin': kelvin,
                            'data': {
                                'mode': 'single_color',
                                'input_color': normalized_color,
                            },
                        },
                    ).start()

                elif device['type'] == 'wled':
                    threading.Thread(
                        target=self.set_wled_color,
                        args=(),
                        kwargs={
                            'wled': device,
                            'rgb': normalized_color,
                        },
                    ).start()
                elif device['type'] == 'ds4':
                    try:
                        threading.Thread(
                            target=self.set_ds4_color,
                            args=[],
                            kwargs={
                                'lightbar_color': normalized_color,
                                'path': self.ds4_paths[device['device_num']]
                            },
                        ).start()
                    except KeyError:
                        device['enabled'] = False

    def rainbow_road(self, values, scale=360):
        movement = np.sum([
            self.data_conversion(value, values.min(), values.max()) * self.acceleration_weight[index]
            for index, value in enumerate(values)
        ])

        if movement > 0:
            self.rainbow_offset += movement

        if self.rainbow_offset > scale:
            self.rainbow_offset -= scale

        for device in self.devices:
            if device['enabled']:
                if device['type'] in ('esp', 'wled'):
                    ip = device['ip']
                    port = device['port']
                    leds = device['leds']
                    brightness = device['brightness']
                    kelvin = device['kelvin']

                    rainbow = [[
                            int(color * 255) for color in colorsys.hsv_to_rgb(
                                ((scale * index / leds) + self.rainbow_offset) / scale, 1, 1
                            )
                        ] for index in range(leds)
                    ]

                    if device['type'] == 'esp':
                        threading.Thread(
                            target=self.set_esp_colors,
                            args=(),
                            kwargs={
                                'ip': ip,
                                'port': port,
                                'brightness': brightness,
                                'kelvin': kelvin,
                                'data': {
                                    'mode': 'streamline',
                                    'led_list': rainbow,
                                    'offset': 0,
                                    'current_length': leds,
                                },
                            },
                        ).start()

                    if device['type'] == 'wled':
                        threading.Thread(
                            target=self.set_wled_strip,
                            args=(),
                            kwargs={
                                'wled': device,
                                'data': rainbow,
                            },
                        ).start()

    def loop(self):
        values = self.pulseviz_bands.values

        if self.mode == 'intensity':
            self.intensity_mode(values)
        elif self.mode == 'rainbow road':
            self.rainbow_road(values)
