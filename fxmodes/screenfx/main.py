import threading
from math import sqrt

import numpy as np

from PIL import ImageGrab
from screeninfo import get_monitors

from common import Common

try:
    from .custom_cutouts import custom_cutouts
except ModuleNotFoundError:
    def custom_cutouts(w, h):
        return {}


class ScreenFX(Common):
    name = 'ScreenFX'

    target_versions = ['dev']
    target_platforms = ['all']

    def __init__(self, used_cutouts, *args, **kwargs):
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
                'top': (0, 0, w, h * 0.11),
                'center': (w/2 - 16, h/2 - 16, w/2 + 16, h/2 + 16),
            },
            'medium': {
                'left': (0, 0, w - w * 0.86, h),
                'right': (w * 0.86, 0, w, h),
                'bottom': (0, h - h * 0.22, w, h),
                'top': (0, 0, w, h * 0.22),
                'center': (w/2 - 32, h/2 - 32, w/2 + 32, h/2 + 32),
            },
            'high': {
                'left': (0, 0, w - w * 0.8, h),
                'right': (w * 0.8, 0, w, h),
                'bottom': (0, h - h * 0.33, w, h),
                'top': (0, 0, w, h * 0.33),
                'center': (w/2 - 64, h/2 - 64, w/2 + 64, h/2 + 64),
            },
        }

        self.cutouts = {
            **cutout_presets[self.config.get('preset', 'medium')],
            **custom_cutouts(w, h),
        }

    def splash(self):
        print('Welcome to ----------------------------------------')
        print('         ██  ██ ██  ███ ███ ██  █ ███ ██ ██        ')
        print('        █   █   █ █ █   █   █ █ █ █    █ █         ')
        print('         █  █   ██  ██  ██  █ █ █ ██    █          ')
        print('          █ █   █ █ █   █   █ █ █ █    █ █         ')
        print('        ██   ██ █ █ ███ ███ █  ██ █   ██ ██        ')
        print('---------------------------------------- by MaWalla')

    def process_image(self, image, cutout):
        if cutout in ['left', 'right']:
            axis = 1
        else:
            axis = 0

        crop = image.crop(self.cutouts[cutout])
        cv_area = np.array(crop)
        average = cv_area.mean(axis=axis)
        return average

    def esp_processing(self, esp, pixel_data):
        ip = esp['ip']
        port = esp['port']
        leds = esp['leds']
        brightness = esp['brightness']
        cutout = esp['cutout']
        flip = esp['flip']
        sections = esp['sections']
        kelvin = esp['kelvin']

        average = np.array_split(pixel_data[cutout], leds, axis=0)
        if flip:
            average = np.flip(average)
        average = np.array_split(average, sections)

        offset = 0
        for section in range(sections):
            average_section = average[section]
            current_section_length = len(average_section)
            self.set_esp_colors(
                ip,
                port,
                brightness,
                kelvin,
                data={
                    'mode': 'streamline',
                    'led_list': [rgb.mean(axis=0).astype(int).tolist() for rgb in average_section],
                    'offset': offset,
                    'current_length': current_section_length,
                }
            )

            offset += current_section_length

    def wled_processing(self, wled, pixel_data):
        ip = wled['ip']
        port = wled['port']
        leds = wled['leds']
        brightness = wled['brightness']
        cutout = wled['cutout']

        average = np.array_split(pixel_data[cutout], leds, axis=0)
        data = [np.array(value.mean(axis=0) * brightness).astype(int) for value in average]

        color_correction = []
        for rgb in data:
            rgb[1] = int((sqrt(rgb[1]) ** 1.825) + (rgb[1] / 100))
            rgb[2] = int((sqrt(rgb[2]) ** 1.775) + (rgb[2] / 100))
            color_correction.append(rgb)

        self.set_wled_colors(ip, port, color_correction)

    def loop(self):
        image = ImageGrab.grab()
        pixel_data = {cutout: self.process_image(image, cutout) for cutout in self.used_cutouts}

        for device in self.devices:
            if device['enabled']:
                if device['type'] == 'esp':
                    threading.Thread(
                        target=self.esp_processing,
                        args=(),
                        kwargs={
                            'esp': device,
                            'pixel_data': pixel_data,
                        },
                    ).start()

                elif device['type'] == 'wled':
                    threading.Thread(
                        target=self.wled_processing,
                        args=(),
                        kwargs={
                            'wled': device,
                            'pixel_data': pixel_data,
                        },
                    ).start()

                elif device['type'] == 'ds4':
                    cutout = device['cutout']
                    try:
                        threading.Thread(
                            target=self.set_ds4_color,
                            args=[],
                            kwargs={
                                'lightbar_color': np.mean(pixel_data[cutout], axis=0).astype(int).tolist(),
                                'path': self.ds4_paths[device['device_num']]
                            },
                        ).start()
                    except KeyError:
                        device['enabled'] = False

                elif device['type'] == 'razer':
                    average_razer = np.array_split(pixel_data['bottom'], device['openrazer'].cols, axis=0)
                    threading.Thread(
                        target=device['openrazer'].chroma_draw,
                        args=(),
                        kwargs={
                            'data': average_razer
                        },
                    ).start()


