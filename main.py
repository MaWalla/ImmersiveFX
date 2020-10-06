import json
import socket
import glob
from time import sleep, time

from pulse import PulseViz
from razer import Razer
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


# integer value, sets the fps. reducing this value reduces strain on cpu
# provides a sane default of 60, which should keep modern CPUs busy :D
fps = config.get('fps', 60)

if fps <= 0:
    print('FPS must be set to at least 1.')
    exit()


# boolean, decides on whether to run the loop though time measurement or not
benchmark = config.get('benchmark')


# string, defines the cutout size from the screen border towards the inside
# can be 'low', 'medium' or 'high'. High puts the most load on the CPU,
# but offers more detail. This setting can also be subject to personal preference.
preset = config.get('preset') or 'medium'


# string, pulseaudio sink name for capturing audio data
# options can be obtained with pactl list sources | grep 'Name:'
source_name = config.get('source_name')


devices = config.get('devices')


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def process_device_config():
    """
    Check if the device configs are complete and optimize the script to their cutouts
    """

    if not devices:
        print('You didn\'t define devices in your config, which renders this script kinda useless')
        exit()

    required_keys = {
        'esp': {'ip', 'port', 'leds', 'cutout'},
        'ds4': {'device_num', 'cutout'},
        'razer': {'cutout'},
    }

    final_devices = []
    used_cutouts = []

    for name, device in devices.items():
        device_type = device.get('type')
        if not device_type:
            print(f'WARNING: you didn\'t define the device type for "{name}", skipping it.')
        else:
            if not device_type in required_keys.keys():
                print(f'WARNING: device {name} has an invalid type, must be {required_keys.keys()}, skipping it')
            else:
                if not (required_keys.get(device_type) - device.keys()):
                    cutout = device.get('cutout')  # defined here cause we'll need that later

                    device_config = {
                        'type': device_type,
                        'enabled': device.get('enabled', True),
                        'brightness': device.get('brightness', 1),
                        'kelvin': device.get('kelvin', 3800),
                        'flip': device.get('flip', False),
                        'cutout': cutout,
                    }

                    if device_type == 'esp':
                        device_config = {
                            'ip': device.get('ip'),
                            'port': device.get('port'),
                            'leds': device.get('leds'),
                            'sections': device.get('sections', 1),
                            **device_config,
                        }
                    if device_type == 'ds4':
                        device_config = {
                            'device_num': device.get('device_num'),
                            **device_config,
                        }

                    if device_type == 'razer':
                        device_config = {
                            'openrazer': Razer(),
                            **device_config
                        }

                    final_devices.append(device_config)

                    if cutout not in used_cutouts:
                        used_cutouts.append(cutout)
                else:
                    print(f'WARNING: device {name} lacks  one of these keys: '
                          f'{required_keys.get(device_type)} skipping it.')

    return final_devices, used_cutouts


final_devices, used_cutouts = process_device_config()


ds4_paths = {counter + 1: path for counter, path in enumerate(glob.glob('/sys/class/leds/0005:054C:05C4.*:global'))}


if fxmode == 'screenfx':
    fx = ScreenFX(
        sock=sock,
        preset=preset,
        ds4_paths=ds4_paths,
        devices=final_devices,
        used_cutouts=used_cutouts,
    )

elif fxmode == 'pulseviz':
    fx = PulseViz(
        sock=sock,
        ds4_paths=ds4_paths,
        source_name=source_name,
        devices=final_devices,
    )
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
print('There are %s devices configured.' % len(final_devices))
print('The FPS are set to %s.' % fps)
print('---------------------------------------------------')


def timed(method):
    start = time()
    method()
    elapsed = (time() - start) * 1000
    print('Cycle took %s ms' % elapsed)


while True:
    sleep(1 / fps)

    if benchmark:
        timed(fx.loop)
    else:
        fx.loop()
