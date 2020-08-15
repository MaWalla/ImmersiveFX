import json
import math
import threading
import numpy as np

from pulseviz import bands


class PulseViz:

    def __init__(self, sock, nodemcus, steps, source_name):
        self.sock = sock
        self.nodemcus = nodemcus

        self.band_mapping = {
            step: [
                np.clip(255 * math.cos(3.1415926535 / steps * step), 0, 255),
                255 * math.sin(3.1415926535 / steps * step),
                np.clip(255 * math.cos(3.1415926535 / steps * step) * -1, 0, 255),
                ]
            for step in range(steps)
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

    def loop(self):
        flipped_min = self.pulseviz_bands.values.min() * -1

        converted_values = [
            [((value + flipped_min) / flipped_min) * color for color in self.band_mapping.get(num)]
            for num, value in enumerate(self.pulseviz_bands.values)
        ]

        converted_color = np.clip(np.amax(converted_values, axis=0).astype(int), 0, 255).tolist()

        # color_value = np.mean(converted_values, axis=0)

        for nodemcu in self.nodemcus:
            ip = nodemcu.get('ip')
            port = nodemcu.get('port')

            threading.Thread(
                target=self.sock.sendto,
                args=(
                    bytes(self.draw(converted_color), 'utf-8'), (ip, port)
                ),
                kwargs={}
            ).start()

    @staticmethod
    def draw(color):
        return json.dumps(
            {'single_color': {
                'input_color': color,
                'kelvin': 3600,
            }}
        )
