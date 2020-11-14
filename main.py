import sys
import json
import socket
import glob
from time import sleep

from benchmark import benchmark
from fxmodes import PulseViz, ScreenFX
from fxmodes.pulseviz import pacmd
from razer import Razer

VERSION = 'dev'  # TODO find a better way than this


try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    print('There is a config.json.example to use as starting point.')
    exit()


# string, decides what to display. screenfx should be cross platform while pulseviz is linux only
valid_fxmodes = ['screenfx', 'pulseviz']
fxmode = config.get('fxmode')

if not fxmode:
    print('No FXMode was found inside your config. No big deal, you can pick it now:\n')
    for index, mode in enumerate(valid_fxmodes):
        print(f'{index}: {mode}')

    choice = input()

    try:
        fxmode = valid_fxmodes[int(choice)]
    except (IndexError, ValueError):
        print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(valid_fxmodes)}, exiting...')
        exit()

if fxmode == 'pulseviz':
    sources = pacmd.list_sources()
    if not config.get('source_name') in sources:
        print('---------------------------------------------------')
        print('PulseViz requires an audio source but no source_name was defined ')
        print('or the source isn\'t available right now. Pick another source please:\n')
        for index, source in enumerate(sources):
            print(f'{index}: {source}')

        choice = input()

        try:
            config['source_name'] = sources[int(choice)]
        except (IndexError, ValueError):
            print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(sources)}, exiting...')
            exit()

    if not config.get('pulseviz_mode') in PulseViz.modes:
        print('---------------------------------------------------')
        print('No PulseViz visualisation was defined ')
        print('pick one now:\n')
        for index, source in enumerate(PulseViz.modes):
            print(f'{index}: {source}')

        choice = input()

        try:
            config['pulseviz_mode'] = PulseViz.modes[int(choice)]
        except (IndexError, ValueError):
            print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(PulseViz.modes)}, ')
            print(f'defaulting to {PulseViz.modes[0]}. ')
            config['pulseviz_mode'] = PulseViz.modes[0]

# integer value, sets the fps. reducing this value reduces strain on cpu
# provides a sane default of 60, which should keep modern CPUs busy :D
fps = config.get('fps', 60)

if fps <= 0:
    print('FPS must be set to at least 1.')
    exit()


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

# TODO move more power to the fxmodes
params = {
    'sock': sock,
    'ds4_paths': ds4_paths,
    'devices': final_devices,
    'preset': preset,
    'used_cutouts': used_cutouts,
    'mode': config.get('pulseviz_mode'),
    'source_name': source_name,
    'flags': sys.argv,
    'core_version': VERSION,
}


if fxmode == 'screenfx':
    fx = ScreenFX(**params)

elif fxmode == 'pulseviz':
    fx = PulseViz(**params)
    fx.start_bands()
else:
    print('No valid fxmode set, please pick screenfx or pulseviz')
    exit()

print('')
print('ImmersiveFX Core version %s' % VERSION)
print('There are %s devices configured.' % len(final_devices))
print('The FPS are set to %s.' % fps)
print('---------------------------------------------------')

if '--benchmark' in sys.argv:
    benchmark(fx)

else:
    while True:
        sleep(1 / fps)
        fx.loop()
