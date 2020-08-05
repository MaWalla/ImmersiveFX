import json
import socket
from time import sleep
from screeninfo import get_monitors

from PIL import ImageGrab
import numpy as np

from razer import chroma_init, chroma_draw

monitor = get_monitors()[0]  # for now, just take the first one's boundaries
w = monitor.width   # shortcuts
h = monitor.height  # more shortcuts yay

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

points = 53

cutouts = {
    'left': (0, 0, w - w * 0.8, h),
    'right': (w * 0.8, 0, w, h),
    'center': (0, h - h * 0.33, w, h),
}

# Razer stuff
device, rows, cols = chroma_init()


def process_image(cutout, sections, axis=0):
    image = ImageGrab.grab(cutout)
    cv_area = np.array(image)
    # # Convert RGB to BGR
    # cv_area = cv_area[:, :, ::-1].copy()
    average = cv_area.mean(axis=axis)
    average_sections_mcu = np.array_split(average, sections, axis)
    average_sections_razer = np.array_split(average, cols, axis)

    return average_sections_mcu, average_sections_razer


def nodemcu_prep(data):
    return json.dumps(
        {'individual': {
            'led_list': {step: rgb.mean(axis=0).astype(int).tolist() for step, rgb in enumerate(np.flip(data))}
        }}
    )


def imageloop():
    average_sections_mcu, average_sections_razer = process_image(cutouts.get('center'), points)
    chroma_draw(average_sections_razer, device, rows, cols)
    sock.sendto(bytes(nodemcu_prep(average_sections_mcu), 'utf-8'), ('192.168.23.10', 13321))


while True:
    # sleep(0.07)
    imageloop()
