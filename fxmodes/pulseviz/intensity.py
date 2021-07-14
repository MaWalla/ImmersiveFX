import threading
import numpy as np

from .main import PulseViz


class Intensity(PulseViz):
    name = 'PulseViz (Intensity)'

    def __init__(self, *args, **kwargs):
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

        super().__init__(*args, **kwargs)

    def loop(self):
        values = super().loop()
        self.intensity_mode(values)

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
                if device['type'] == 'wled':
                    threading.Thread(
                        target=self.set_wled_color,
                        args=(),
                        kwargs={
                            'wled': device,
                            'rgb': normalized_color,
                        },
                    ).start()

                if device['type'] == 'arduino':
                    threading.Thread(
                        target=self.set_arduino_color,
                        args=(),
                        kwargs={
                            'arduino': device,
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
