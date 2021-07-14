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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def parse_devices(self, config):
        # strip away the device names and make it a list,
        # since we won't need em, but a bit of extra performance is nice!
        return [device for name, device in super().parse_devices(config).items()]

    def splash(self):
        print('Welcome to ----------------------------- by MaWalla')
        print('        ███ █  █ █    ██ ███ █   █ ███ ████        ')
        print('        █ █ █  █ █   █   █   █   █  █     █        ')
        print('        ███ █  █ █    █  ██  ██ ██  █   ██         ')
        print('        █   █  █ █     █ █    ███   █  █           ')
        print('        █    ██  ███ ██  ███   █   ███ ████        ')
        print('-- backend: https://github.com/pckbls/pulseviz.py -')

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

    def loop(self):
        return self.pulseviz_bands.values

    @staticmethod
    def data_conversion(value, minimum, maximum):
        multiplicator = (value - minimum) / (maximum - minimum)
        return multiplicator * multiplicator * multiplicator
