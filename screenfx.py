import os
import json
import threading
import numpy as np

from PIL import ImageGrab
from screeninfo import get_monitors


class ScreenFX:

    def __init__(self, sock, kelvin, razer_enabled, ds4_enabled, ds4_paths, nodemcus, used_cutouts, preset):
        self.sock = sock
        self.kelvin = kelvin
        self.razer_enabled = razer_enabled
        self.ds4_enabled = ds4_enabled
        self.ds4_paths = ds4_paths
        self.nodemcus = nodemcus
        self.used_cutouts = used_cutouts

        if razer_enabled:
            from razer import chroma_init, chroma_draw
            self.device, self.rows, self.cols = chroma_init()
            self.chroma_draw = chroma_draw

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
            **cutout_presets.get(preset)
        }

    def process_image(self, image, cutout):
        if cutout in ['left', 'right']:
            axis = 1
        else:
            axis = 0

        crop = image.crop(self.cutouts.get(cutout))
        cv_area = np.array(crop)
        average = cv_area.mean(axis=axis)
        return average

    def loop(self):
        image = ImageGrab.grab()
        pixel_data = {cutout: self.process_image(image, cutout) for cutout in self.used_cutouts}

        if self.razer_enabled:
            average_razer = np.array_split(pixel_data.get('bottom'), self.cols, axis=0)
            self.chroma_draw(average_razer, self.device, self.rows, self.cols)

        if self.ds4_enabled and self.ds4_paths:
            threading.Thread(
                target=self.set_ds4_color,
                args=[],
                kwargs={
                    'ds4_paths': self.ds4_paths,
                    'pixel_data': pixel_data,
                },
            ).start()

        for nodemcu in self.nodemcus:
            ip = nodemcu.get('ip')
            port = nodemcu.get('port')
            leds = nodemcu.get('leds')
            cutout = nodemcu.get('cutout')
            flip = nodemcu.get('flip')

            threading.Thread(
                target=self.sock.sendto,
                args=(
                    bytes(self.prepare_data(pixel_data, leds, cutout, flip), 'utf-8'), (ip, port)
                ),
                kwargs={},
            ).start()

    @staticmethod
    def set_ds4_color(ds4_paths, pixel_data):
        lightbar_color = np.mean(pixel_data.get('center'), axis=0).astype(int).tolist()
        red, green, blue = lightbar_color

        for controller in ds4_paths:
            red_path = f'{controller[:-6]}red/brightness'
            green_path = f'{controller[:-6]}green/brightness'
            blue_path = f'{controller[:-6]}blue/brightness'

            r = open(red_path, 'w')
            r.write(str(red))
            r.close()

            g = open(green_path, 'w')
            g.write(str(green))
            g.close()

            b = open(blue_path, 'w')
            b.write(str(blue))
            b.close()

    def prepare_data(self, pixel_data, leds, cutout, flip):
        average = pixel_data.get(cutout)
        average_mcu = np.array_split(average, leds, axis=0)

        if flip:
            average_mcu = np.flip(average_mcu)

        return json.dumps(
            {'streamline': {
                'led_list': [rgb.mean(axis=0).astype(int).tolist() for rgb in average_mcu],
                'kelvin': self.kelvin,
            }}
        )
