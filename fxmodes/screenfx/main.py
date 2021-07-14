import threading
import numpy as np

from PIL import ImageGrab
from screeninfo import get_monitors

from immersivefx import Core

try:
    from .custom_cutouts import custom_cutouts
except ModuleNotFoundError:
    def custom_cutouts(w, h):
        return {}


class ScreenFX(Core):
    name = 'ScreenFX'

    target_versions = ['dev']
    target_platforms = ['all']

    def __init__(self, *args, config, **kwargs):
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
            **cutout_presets[config.get('preset', 'medium')],
            **custom_cutouts(w, h),
        }
        self.used_cutouts = set()

        super().__init__(*args, config=config, **kwargs)

    def parse_devices(self, config):
        # this will give us a dict of dicts containg the device config, we can extend it!
        # for recognition purposes each device is named
        base_devices = super().parse_devices(config)

        # We'll turn the device config into a list here on purpose since the name isn't needed in this case
        screenfx_devices = []

        devices = config.get('devices')

        for name, device_config in base_devices.items():
            cutout = devices.get(name).get('cutout')

            if cutout:
                if cutout in self.cutouts:
                    self.used_cutouts = {*self.used_cutouts, cutout}
                    screenfx_devices.append({**device_config, 'cutout': cutout})
                else:
                    print(f'Device {name} has an invalid cutout. If its a custom one, please make sure')
                    print('its specified in custom_cutouts.py')
                    exit(1)
            else:
                print(f'Device {name} is missing the cutout key, which is required for ScreenFX though, skipping it.')
                exit(1)

        if not screenfx_devices:
            print('ScreenFX is missing valid devices, perhaps none of them have a cutout specified? Exiting...')
            exit(1)

        return screenfx_devices

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

    def wled_processing(self, wled, pixel_data):
        leds = wled['leds']
        brightness = wled['brightness']
        flip = wled['flip']
        cutout = wled['cutout']

        average = np.array_split(pixel_data[cutout], leds, axis=0)
        if flip:
            # I think this causes a deprecation warning btw.
            average = np.flip(average)

        data = [np.array(value.mean(axis=0) * brightness).astype(int) for value in average]

        if wled['color_correction']:
            color_correction = []
            for rgb in data:
                color_correction.append(self.color_correction(rgb))
            self.set_wled_strip(wled, color_correction)
        else:
            self.set_wled_strip(wled, data)


    def loop(self):
        image = ImageGrab.grab()
        pixel_data = {cutout: self.process_image(image, cutout) for cutout in self.used_cutouts}

        for device in self.devices:
            if device['enabled']:
                if device['type'] == 'wled':
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
