import json
import threading
from time import time

import numpy as np

from PIL import ImageGrab
from screeninfo import get_monitors

from common import Common


class ScreenFX(Common):

    def __init__(self, used_cutouts, preset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.used_cutouts = used_cutouts

        monitor = get_monitors()[0]  # for now, just take the first one's boundaries
        w = monitor.width   # shortcuts
        h = monitor.height  # more shortcuts yay

        cutout_presets = {
            'low': {
                'left': (0, 0, w - w * 0.92, h),
                'right': (w * 0.92, 0, w, h),
                'bottom': (0, h - h * 0.11, w, h),
            },
            'medium': {
                'left': (0, 0, w - w * 0.86, h),
                'right': (w * 0.86, 0, w, h),
                'bottom': (0, h - h * 0.22, w, h),
            },
            'high': {
                'left': (0, 0, w - w * 0.8, h),
                'right': (w * 0.8, 0, w, h),
                'bottom': (0, h - h * 0.33, w, h),
            },
        }

        self.cutouts = {
            'center': (w/2 - 32, h/2 - 32, w/2 + 32, h/2 + 32),
            **cutout_presets[preset]
        }

    def process_image(self, image, cutout):
        if cutout in ['left', 'right']:
            axis = 1
        else:
            axis = 0

        crop = image.crop(self.cutouts[cutout])
        cv_area = np.array(crop)
        average = cv_area.mean(axis=axis)
        return average

    def loop(self):
        image = ImageGrab.grab()
        pixel_data = {cutout: self.process_image(image, cutout) for cutout in self.used_cutouts}

        if self.razer_enabled:
            average_razer = np.array_split(pixel_data['bottom'], self.cols, axis=0)
            self.chroma_draw(average_razer, self.device, self.rows, self.cols)

        if self.ds4_enabled and self.ds4_paths:
            threading.Thread(
                target=self.set_ds4_color,
                args=[],
                kwargs={
                    'lightbar_color': np.mean(pixel_data['center'], axis=0).astype(int).tolist(),
                },
            ).start()

        for nodemcu in self.nodemcus:
            threading.Thread(
                target=self.nodemcu_colors,
                args=(),
                kwargs={
                    'nodemcu': nodemcu,
                    'pixel_data': pixel_data,
                },
            ).start()

    def nodemcu_colors(self, nodemcu, pixel_data):
        ip = nodemcu['ip']
        port = nodemcu['port']
        leds = nodemcu['leds']
        cutout = nodemcu['cutout']
        flip = nodemcu['flip']
        sections = nodemcu['sections']

        average = np.array_split(pixel_data[cutout], leds, axis=0)
        if flip:
            average = np.flip(average)
        average = np.array_split(average, sections)

        offset = 0

        for section in range(sections):
            average_section = average[section]
            current_section_length = len(average_section)
            self.sock.sendto(
                bytes(self.nodemcu_data(average_section, offset, current_section_length), 'utf-8'), (ip, port)
            )
            offset += current_section_length

    def nodemcu_data(self, average, offset, current_length):
        return json.dumps({
            'mode': 'streamline',
            'offset': offset,
            'current_length': current_length,
            'led_list': [rgb.mean(axis=0).astype(int).tolist() for rgb in average],
            'kelvin': self.kelvin,
        })
