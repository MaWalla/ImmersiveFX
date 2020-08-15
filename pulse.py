import json
import threading
import numpy as np

from pulseviz import bands

fixture = {
    'source_name': 'alsa_output.pci-0000_00_1b.0.analog-stereo.monitor',
    'sample_frequency': 44100,
    'sample_size': 8192,
    'window_size': 1024,
    'window_overlap': 0.5,
    'window_function': 'hanning',
    'weighting': 'Z',
    'band_frequencies': bands.calculate_octave_bands(fraction=3)
}

steps = 33

band_mapping = {
    step: [
        (255 / steps) * (steps - step),
        0,
        (255 / steps) * step,
    ]
    for step in range(steps)
}

band = bands.Bands(**fixture)
band.start()


def draw(color):
    return json.dumps(
        {'single_color': {
            'input_color': color,
            'kelvin': 3600,
        }}
    )


def draw_bands(sock, nodemcus):


    flipped_min = band.values.min() * -1

    converted_values = [
        [((value + flipped_min) / flipped_min) * color for color in band_mapping.get(num)]
        for num, value in enumerate(band.values)
    ]

    converted_color = np.clip(np.amax(converted_values, axis=0).astype(int), 0, 255).tolist()

    # color_value = np.mean(converted_values, axis=0)

    for nodemcu in nodemcus:
        ip = nodemcu.get('ip')
        port = nodemcu.get('port')
        leds = nodemcu.get('leds')
        cutout = nodemcu.get('cutout')
        flip = nodemcu.get('flip')

        threading.Thread(
            target=sock.sendto,
            args=(
                bytes(draw(converted_color), 'utf-8'), (ip, port)
            ),
            kwargs={}
        ).start()
