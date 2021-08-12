import os
import sys
import json
from time import sleep

VERSION = '1.0.0'  # TODO find a better way than this, grabbing git tags perhaps

try:
    with open('config.json') as file:
        config = json.load(file)
except FileNotFoundError:
    print('config file not found. you need to place config.json into the main.py directory.')
    print('There is a config.json.example to use as starting point.')
    exit()


script_path, *_ = sys.argv
base_dir = os.path.dirname(script_path)
fxmode_path = os.path.join(base_dir, 'fxmodes')

available_fxmodes = {}

for fxmode in os.listdir(fxmode_path):
    try:
        modes = getattr(__import__(f'fxmodes.{fxmode}', globals(), locals(), [fxmode]), 'modes')

        for mode in modes:
            available_fxmodes = {
                **available_fxmodes,
                mode.name: mode,
            }
    except (ModuleNotFoundError, AttributeError):
        continue

valid_fxmodes = list(available_fxmodes)
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


params = {
    'version': VERSION,
    'config': config,
    'flags': sys.argv,
    'core_version': VERSION,
}

fxmode = selected_fxmode(**params)

print('')
print('ImmersiveFX Core version %s' % VERSION)
print('---------------------------------------------------')

while True:
    # the main thread must stay alive and should do as little as possible from this point on
    # in the future we may put some control mechanisms for the FXMode here, but
    # heavy lifting is done by the data thread and sending by device threads
    sleep(5)
