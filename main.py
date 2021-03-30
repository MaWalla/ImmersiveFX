import sys
import json
from time import sleep

from benchmark import benchmark
from fxmodes import available_fxmodes

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

params = {
    'config': config,
    'flags': sys.argv,
    'core_version': VERSION,
}

fxmode = selected_fxmode(**params)

print('')
print('ImmersiveFX Core version %s' % VERSION)
print('---------------------------------------------------')

if '--benchmark' in sys.argv:
    benchmark(fxmode)

else:
    while True:
        sleep(1 / fps)
        fxmode.loop()
