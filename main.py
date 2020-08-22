import json
import socket
import glob
from time import sleep, time

from pulse import PulseViz
from screenfx import ScreenFX

try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    print('There is a config.json.example to use as starting point.')
    exit()


# string, decides what to display. screenfx should be cross platform while pulseviz is linux only
valid_fxmodes = ['screenfx', 'pulseviz']
fxmode = config.get('fxmode') if config.get('fxmode') in valid_fxmodes else 'screenfx'


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


# enables or disables support for ds4 controllers. Linux only.
# copy and ds4perm to /opt/ and make it executable.
# also copy 10-local.rules to /etc/udev/rules.d/ and run
# finally run sudo udevadm control --reload-rules && sudo udevadm trigger
# or reboot
ds4_enabled = config.get('ds4')


# string, defines the cutout size from the screen border towards the inside
# can be 'low', 'medium' or 'high'. High puts the most load on the CPU,
# but offers more detail. This setting can also be subject to personal preference.
preset = config.get('preset') or 'medium'


# string, pulseaudio sink name for capturing audio data
# options can be obtained with pactl list sources | grep 'Name:'
source_name = config.get('source_name')


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
# DualShock 4 prepopulates it with center
used_cutouts = []
if razer_enabled:
    used_cutouts += ['bottom']
if ds4_enabled:
    used_cutouts += ['center']


if fps and fps < 0:
    print('Please set the fps to 0 or above or remove the option.')
    print('Last time I checked, time travel wasn\'t a thing yet.')
    exit()


if not razer_enabled and not ds4_enabled and not nodemcus:
    print('No devices. Either set |"razer": true| or |"ds4": true| in the config or define at least one NodeMCU')
    exit()


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

if ds4_enabled:
    ds4_paths = [path for path in glob.glob('/sys/class/leds/0005:054C:05C4.*:global')]
else:
    ds4_paths = []


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

if fxmode == 'screenfx':
    fx = ScreenFX(sock, kelvin, razer_enabled, ds4_enabled, ds4_paths, nodemcus, used_cutouts, preset)

elif fxmode == 'pulseviz':
    fx = PulseViz(sock, nodemcus, kelvin, 33, source_name)
    fx.start_bands()
else:
    print('No valid fxmode set, please pick screenfx or pulseviz')
    exit()

print('Welcome to ----------------------------------------')
print('███ █   █ █   █ ███ ██   ██ ███ █   █ ███ ███ ██ ██')
print(' █  ██ ██ ██ ██ █   █ █ █    █  █   █ █   █    █ █ ')
print(' █  █ █ █ █ █ █ ██  ██   █   █  ██ ██ ██  ██    █  ')
print(' █  █   █ █   █ █   █ █   █  █   ███  █   █    █ █ ')
print('███ █   █ █   █ ███ █ █ ██  ███   █   ███ █   ██ ██')
print('-----------------------------------------by MaWalla')
print('For visualisation, you\'ve picked: %s.' % fxmode)
print('You %s Razer support.' % ('enabled' if razer_enabled else 'disabled'))
print('You %s DualShock 4 support.' % ('enabled' if ds4_enabled else 'disabled'))
print('There are %s NodeMCUs configured.' % len(nodemcus))
print('The FPS are set to %s.' % (fps if fps else 'unlimited'))
print('---------------------------------------------------')


def timed(method):
    start = time()
    method()
    elapsed = (time() - start) * 1000
    print('Cycle took %s ms' % elapsed)


while True:
    if fps:
        sleep(1 / fps)

        if benchmark:
            timed(fx.loop)
        else:
            fx.loop()
