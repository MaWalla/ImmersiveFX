import json
import socket
import threading
from time import sleep, time
from screeninfo import get_monitors

from PIL import ImageGrab
import numpy as np

from pulse import get_bands

try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    exit()

# integer value, sets the fps. 0 for not setting it means unlimited fps
# reducing this value reduces strain on cpu
fps = config.get('fps')


# boolean, decides on whether to run the loop though time measurement or not
benchmark = config.get('benchmark') or False


# integer, ranges from 1000 to 12000 in steps of 100.
# so far only affects NodeMCUs
kelvin = config.get('kelvin')


# decides on whether to use support for razer keyboards or not.
# Currently supported is the Razer Blackwidow Chroma 2014. Needs openrazer.
razer_enabled = config.get('razer')


# string, defines the cutout size from the screen border towards the inside
# can be 'low', 'medium' or 'high'. High puts the most load on the CPU,
# but offers more detail. This setting can also be subject to personal preference.
preset = config.get('preset') or 'medium'


# Takes a list of dicts(objects). Each one needs the following keys:
# id: string to identify the device
# ip: string ip address of the nodemcu in the network
# port: integer UDP port the nodemcu listens on
# leds: integer amount of leds connected to it
# flip: boolean, switches beginning and end to fit your need and setup
# cutout: string which part of the screen to use for the color display
# can be: left, right or bottom
nodemcus = config.get('nodemcus')


# This list gets populated during processing the nodemcu config.
# if Razer is in use, it gets prepopulated with bottom.
used_cutouts = ['bottom'] if razer_enabled else []


if fps and fps < 0:
    print('Please set the fps to 0 or above or remove the option.')
    print('Last time I checked, time travel wasn\'t a thing yet.')
    exit()


if not razer_enabled and not nodemcus:
    print('No devices. Either set |"razer": true| in the config or define at least one NodeMCU')
    exit()

if razer_enabled:
    from razer import chroma_init, chroma_draw
    device, rows, cols = chroma_init()


def process_nodemcu_config():
    """
    If there are NodeMCUs configured, checks if their configs are complete and optimize the script to their cutouts
    """
    if not nodemcus:
        return None

    for nodemcu in nodemcus:
        id = nodemcu.get('id')
        ip = nodemcu.get('ip')
        port = nodemcu.get('port')
        leds = nodemcu.get('leds')
        cutout = nodemcu.get('cutout')
        flip = nodemcu.get('flip')

        if not id or not ip or not port or not leds or cutout not in ['left', 'right', 'bottom'] or flip is None:
            print('One or more NodeMCU configs are incomplete. Please fix the file and retry')
            exit()

        if cutout not in used_cutouts:
            used_cutouts.append(cutout)


process_nodemcu_config()


monitor = get_monitors()[0]  # for now, just take the first one's boundaries
w = monitor.width   # shortcuts
h = monitor.height  # more shortcuts yay

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


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


cutouts = {**cutout_presets.get(preset)}


def process_image(image, cutout):
    if cutout in ['left', 'right']:
        axis = 1
    else:
        axis = 0

    crop = image.crop(cutouts.get(cutout))
    cv_area = np.array(crop)
    average = cv_area.mean(axis=axis)
    return average


def nodemcu_draw(pixel_data, leds, cutout, flip):
    average = pixel_data.get(cutout)
    average_mcu = np.array_split(average, leds, axis=0)

    if flip:
        average_mcu = np.flip(average_mcu)

    return json.dumps(
        {'streamline': {
            'led_list': [rgb.mean(axis=0).astype(int).tolist() for rgb in average_mcu],
            'kelvin': kelvin,
        }}
    )


def imageloop():
    image = ImageGrab.grab()
    pixel_data = {cutout: process_image(image, cutout) for cutout in used_cutouts}

    if razer_enabled:
        average_razer = np.array_split(pixel_data.get('center'), cols, axis=0)
        chroma_draw(average_razer, device, rows, cols)

    for nodemcu in nodemcus:
        ip = nodemcu.get('ip')
        port = nodemcu.get('port')
        leds = nodemcu.get('leds')
        cutout = nodemcu.get('cutout')
        flip = nodemcu.get('flip')

        threading.Thread(
            target=sock.sendto,
            args=(
                bytes(nodemcu_draw(pixel_data, leds, cutout, flip), 'utf-8'), (ip, port)
            ),
            kwargs={}
        ).start()


print('----------------------------------')
print('Welcome to ImmersiveFX')
print('You got Razer support %s ' % ('enabled.' if razer_enabled else 'disabled.'))
print('There are %s NodeMCUs configured.' % len(nodemcus))
print('The FPS are set to %s.' % (fps if fps else 'unlimited'))
print('----------------------------------')


def timed(method):
    start = time()
    method()
    elapsed = (time() - start) * 1000
    print('Cycle took %s ms' % elapsed)


while True:
    # if fps:
    #     sleep(1 / fps)

    # if benchmark:
    #     timed(imageloop)
    # else:
    #     imageloop()

    get_bands()
