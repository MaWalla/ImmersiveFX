"""
My BlackWidow Chroma 2014 as test subject.
No cherry keys were harmed during this experiment
"""
from openrazer.client import DeviceManager


class Razer:

    def __init__(self):
        device_manager = DeviceManager()
        print("Found {} Razer devices".format(len(device_manager.devices)))
        device_manager.sync_effects = False
        for device in device_manager.devices:
            rows, cols = device.fx.advanced.rows, device.fx.advanced.cols
            device.brightness = 100

            #  lets assume there's only one device for now
            self.device = device
            self.rows = rows
            self.cols = cols

    def chroma_draw(self, data):
        # range Y 0-5
        # range X 0-21

        for col in range(self.cols):
            r, g, b, = data[col].mean(axis=0)
            for row in range(self.rows):
                self.device.fx.advanced.matrix[row, col] = r, g, b

        self.device.fx.advanced.draw()
