import json
import math
import threading
import numpy as np

from pulseviz import bands


class PulseViz:

    def __init__(self, sock, nodemcus, kelvin, steps, source_name):
        self.sock = sock
        self.nodemcus = nodemcus
        self.kelvin = kelvin

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



        bands_data = {
            'source_name': source_name,
            'sample_frequency': 44100,
            'sample_size': 8192,
            'window_size': 1024,
            'window_overlap': 0.5,
            'window_function': 'hanning',
            'weighting': 'Z',
            'band_frequencies': bands.calculate_octave_bands(fraction=3)
        }

        self.pulseviz_bands = bands.Bands(**bands_data)

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

    def loop(self):
        values = self.pulseviz_bands.values

        converted_values = [[
                self.data_conversion(value, values.min(), values.max()) * color if not np.isinf(value) else 0
                for color in self.band_mapping.get(num)
            ] for num, value in enumerate(values)
        ]

        color = np.array(converted_values).mean(axis=0)
        normalized_color = np.clip([
            self.post_process_color(rgb, color) for rgb in color
        ], 0, 255).astype(int).tolist()

        for nodemcu in self.nodemcus:
            ip = nodemcu.get('ip')
            port = nodemcu.get('port')

            threading.Thread(
                target=self.sock.sendto,
                args=(
                    bytes(self.prepare_data(normalized_color), 'utf-8'), (ip, port)
                ),
                kwargs={}
            ).start()

    def prepare_data(self, color):
        return json.dumps(
            {'single_color': {
                'input_color': color,
                'kelvin': self.kelvin,
            }}
        )
