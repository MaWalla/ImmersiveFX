import sys
import json
from time import sleep

from benchmark import benchmark
from fxmodes import available_fxmodes
from razer import Razer

VERSION = 'dev'  # TODO find a better way than this


try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    print('There is a config.json.example to use as starting point.')
    exit()


valid_fxmodes = list(available_fxmodes.keys())
selected_fxmode = available_fxmodes.get(config.get('fxmode'))

while not selected_fxmode:
    print('No FXMode was found inside your config. No big deal, you can pick it now:\n')
    for index, mode in enumerate(valid_fxmodes):
        print(f'{index}: {mode}')

    choice = input()

    try:
        selected_fxmode = available_fxmodes.get(valid_fxmodes[int(choice)])
    except (IndexError, ValueError):
        print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(valid_fxmodes)}, try again!')
        exit()

# integer value, sets the fps. reducing this value reduces strain on cpu
# provides a sane default of 60, which should keep modern CPUs busy :D
fps = config.get('fps', 60)

if fps <= 0:
    print('FPS must be set to at least 1.')
    exit()


def process_device_config():
    """
    Check if the device configs are complete and optimize the script to their cutouts
    """
    devices = config.get('devices')

    if not devices:
        print('You didn\'t define devices in your config, which renders this script kinda useless')
        exit()

    required_keys = {
        'wled': {'ip', 'leds', 'cutout'},
        'ds4': {'device_num', 'cutout'},
        'razer': {'cutout'},
    }

    final_devices = []
    used_cutouts = []

    for name, device in devices.items():
        device_type = device.get('type')
        device_enabled = device.get('enabled', True)
        if device_enabled:
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
                            'enabled': device_enabled,
                            'brightness': device.get('brightness', 1),
                            'flip': device.get('flip', False),
                            'cutout': cutout,
                        }
                        if device_type == 'wled':
                            device_config = {
                                'ip': device.get('ip'),
                                'port': device.get('port', 21324),
                                'leds': device.get('leds'),
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


# TODO move more power to the fxmodes
params = {
    'devices': final_devices,
    'used_cutouts': used_cutouts,
    'config': config,
    'flags': sys.argv,
    'core_version': VERSION,
}

fxmode = selected_fxmode(**params)

print('')
print('ImmersiveFX Core version %s' % VERSION)
print('There are %s devices configured.' % len(final_devices))
print('The FPS are set to %s.' % fps)
print('---------------------------------------------------')

if '--benchmark' in sys.argv:
    benchmark(fxmode)

else:
    while True:
        sleep(1 / fps)
        fxmode.loop()
