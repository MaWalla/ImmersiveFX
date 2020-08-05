"""
My BlackWidow Chroma 2014 as test subject.
No cherry keys were harmed during this experiment
"""
from openrazer.client import DeviceManager


def chroma_init():
    device_manager = DeviceManager()
    print("Found {} Razer devices".format(len(device_manager.devices)))
    device_manager.sync_effects = False
    for device in device_manager.devices:
        rows, cols = device.fx.advanced.rows, device.fx.advanced.cols
        device.brightness = 100

        return device, rows, cols


def chroma_draw(data, device, rows, cols):
    # range Y 0-5
    # range X 0-21

    for row in range(rows):
        for col in range(cols):
            r, g, b, = data[col].mean(axis=0)

            device.fx.advanced.matrix[row, col] = r, g, b

    device.fx.advanced.draw()
