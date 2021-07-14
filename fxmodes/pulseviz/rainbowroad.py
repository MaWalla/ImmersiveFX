import colorsys
import threading
import numpy as np

from .main import PulseViz


class RainbowRoad(PulseViz):
    name = 'PulseViz (Rainbow Road)'

    def __init__(self, *args, **kwargs):
        self.rainbow_offset = 0
        self.acceleration_weight = {
            0: 0.25,
            1: 0.33,
            2: 0.5,
            3: 0.75,
            4: 0.83,
            5: 1,
            6: 1,
            7: 0.75,
            8: 0.5,
            9: 0.33,
            10: 0.1,
            11: 0.05,
            **{index + 12: 0 for index in range(21)},
        }

        super().__init__(*args, **kwargs)

    def loop(self):
        values = super().loop()
        self.rainbow_road(values)

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
                if device['type'] == 'wled':
                    leds = device['leds']

                    rainbow = [[
                        int(color * 255) for color in colorsys.hsv_to_rgb(
                            ((scale * index / leds) + self.rainbow_offset) / scale, 1, 1
                        )
                    ] for index in range(leds)
                    ]

                    threading.Thread(
                        target=self.set_wled_strip,
                        args=(),
                        kwargs={
                            'wled': device,
                            'data': rainbow,
                        },
                    ).start()

                if device['type'] == 'arduino':
                    leds = device['leds']

                    rainbow = [[
                        int(color * 255) for color in colorsys.hsv_to_rgb(
                            ((scale * index / leds) + self.rainbow_offset) / scale, 1, 1
                        )
                    ] for index in range(leds)
                    ]

                    threading.Thread(
                        target=self.set_arduino_strip,
                        args=(),
                        kwargs={
                            'data': rainbow,
                        },
                    ).start()
