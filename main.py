import argparse
import os
import sys
import json
from time import sleep

from utils import manage_requirements


VERSION = '1.2.0'  # TODO find a better way than this, grabbing git tags perhaps


parser = argparse.ArgumentParser()

arg_texts = {
    'd': 'skip dependency check on start',
    'p': 'skip platform check for fxmodes',
    's': 'skip version check for fxmodes',
    'f': 'displays frame times per thread. Disables available commands while active',
    't': 'single threaded mode. Slow, but useful for testing/debugging',
}

parser.add_argument('-d', '--no-deps', help=arg_texts.get('d'), action='store_true')
parser.add_argument('-p', '--no-platform-check', help=arg_texts.get('p'), action='store_true')
parser.add_argument('-s', '--no-version-check', help=arg_texts.get('s'), action='store_true')
parser.add_argument('-f', '--display-frametimes', help=arg_texts.get('f'), action='store_true')
parser.add_argument('-t', '--single-threaded', help=arg_texts.get('t'), action='store_true')

args = parser.parse_args()

no_dependency_check = args.no_deps
flags = {
    'no_version_check': args.no_version_check,
    'no_platform_check': args.no_platform_check,
}

if not no_dependency_check:
    if sys.prefix == sys.base_prefix:
        print('Looks like you aren\'t running ImmersiveFX inside a virtual environment')
        print('This will likely cause issues or prevent it from running altogether')
        print()

    else:
        manage_requirements()

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


if not available_fxmodes:
    print('No valid FXModes found, are the dependencies available (e.g. venv activated)? exiting...')
    exit(1)


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

fxmode = selected_fxmode(
    core_version=VERSION,
    config=config,
    launch_arguments=args,
)

print('')
print('ImmersiveFX Core version %s' % VERSION)
print('---------------------------------------------------')

try:
    while True:
        # the main thread must stay alive and should do as little as possible from this point on.
        # heavy lifting is done by the data thread and sending by device threads

        if args.display_frametimes:
            command = ''
            sleep(1)
        else:
            command = input()
        if command == 'reload':
            print('reloading...')
            fxmode.stop()

            try:
                with open('config.json') as file:
                    config = json.load(file)
            except FileNotFoundError:
                print('config file not found. you need to place config.json into the main.py directory.')
                print('There is a config.json.example to use as starting point.')
                exit()

            fxmode = selected_fxmode(
                core_version=VERSION,
                config=config,
                launch_arguments=args,
            )
            print('reload done.')

        if command == 'start':
            print('starting threads...')
            fxmode.start_threads()
            print('started threads.')

        if command == 'stop':
            print('stoppting threads...')
            fxmode.stop()
            print('stopped threads.')

        if command == 'exit':
            print('exiting...')
            fxmode.kill()
            break

except KeyboardInterrupt:
    fxmode.kill()

exit()
