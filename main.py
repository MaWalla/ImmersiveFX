import json
import socket
import threading
from time import sleep
from screeninfo import get_monitors

from PIL import ImageGrab, Image
import numpy as np

try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    exit()

# integer value, sets the fps. 0 for not setting it means unlimited fps
# reducing this value reduces strain on cpu
fps = config.get('fps')
# decides on whether to use support for razer keyboards or not.
# Currently supported is the Razer Blackwidow Chroma 2014. Needs openrazer.
razer_enabled = config.get('razer')
# Takes a list of dicts(objects). Each one needs the following keys:
# id: string to identify the device
# ip: string ip address of the nodemcu in the network
# port: integer UDP port the nodemcu listens on
# leds: integer amount of leds connected to it
# inverse: boolean, set it to true if the led strip goes right-to-left
# cutout: string which part of the screen to use for the color display
# can be: left, right or bottom
nodemcus = config.get('nodemcus')

if not razer_enabled and not nodemcus:
    print('No devices. Either set |"razer": true| or or define at least one nodemcu')
    exit()

if razer_enabled:
    from razer import chroma_init, chroma_draw
    device, rows, cols = chroma_init()


def check_nodemcu_config():
    if not nodemcus:
        return None

    for nodemcu in nodemcus:
        id = nodemcu.get('id')
        ip = nodemcu.get('ip')
        port = nodemcu.get('port')
        leds = nodemcu.get('leds')
        cutout = nodemcu.get('cutout')
        inverse = nodemcu.get('inverse')

        if not id or not ip or not port or not leds or cutout not in ['left', 'right', 'bottom'] or inverse is None:
            print('One or more NodeMCU configs are incomplete. Please fix the file and retry')
            exit()


check_nodemcu_config()


monitor = get_monitors()[0]  # for now, just take the first one's boundaries
w = monitor.width   # shortcuts
h = monitor.height  # more shortcuts yay

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

cutouts = {
    'left': (0, 0, w - w * 0.8, h),
    'right': (w * 0.8, 0, w, h),
    'bottom': (0, h - h * 0.33, w, h),
}


def process_image(cutout):
    if cutout in ['left', 'right']:
        axis = 1
    else:
        axis = 0

    image = ImageGrab.grab(cutouts.get(cutout))
    cv_area = np.array(image)
    average = cv_area.mean(axis=axis)
    return average


def nodemcu_draw(leds, cutout, inverse):
    average = process_image(cutout)
    average_mcu = np.array_split(average, leds, axis=0)

    if inverse and cutout not in ['left', 'right']:
        average_mcu = np.flip(average_mcu)

    return json.dumps(
        {'individual': {
            # streamline doesn't work yet for some reason
            # 'led_list': [rgb.mean(axis=0).astype(int).tolist() for rgb in average_mcu]
            'led_list': {step: rgb.mean(axis=0).astype(int).tolist() for step, rgb in enumerate(average_mcu)}
        }}
    )


def imageloop():
    if razer_enabled:
        average_razer = np.array_split(process_image(cutouts.get('center')), cols, axis=0)
        chroma_draw(average_razer, device, rows, cols)
    for nodemcu in nodemcus:
        ip = nodemcu.get('ip')
        port = nodemcu.get('port')
        leds = nodemcu.get('leds')
        cutout = nodemcu.get('cutout')
        inverse = nodemcu.get('inverse')

        threading.Thread(
            target=sock.sendto,
            args=(
                bytes(nodemcu_draw(leds, cutout, inverse), 'utf-8'), (ip, port)
            ),
            kwargs={}
        ).start()


while True:
    if fps:
        sleep(1 / fps)
    imageloop()
