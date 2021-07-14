import subprocess
import re


class PACmdException(Exception):
    pass


def list_sources():
    result = []

    try:
        process = subprocess.Popen(['pacmd', 'list-sources'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise PACmdException('pacmd could not be found on the system. Is PulseAudio installed?')

    stdout, _ = process.communicate(timeout=10.0)
    if process.returncode != 0:
        raise PACmdException('pacmd exited with return code {0}'.format(process.returncode))

    output = ''.join([line.decode('utf-8') for line in stdout.splitlines(keepends=False)]).split('index')[1:]
    devices = [device.split('\t') for device in output]

    for device in devices:
        name, *_ = [prop for prop in device if 'name: ' in prop]
        device_name, *_ = [prop for prop in device if 'device.product.name = ' in prop]

        yield name[6:].replace('<', '').replace('>', ''), device_name[22:].replace('"', '')
