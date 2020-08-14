from pulseviz import bands

fixture = {
    'source_name': 'alsa_output.pci-0000_00_1b.0.analog-stereo.monitor',
    'sample_size': 2048,
    'window_size': 2048,
    'band_frequencies': bands.calculate_octave_bands(fraction=1)
}


band_mapping = {
    0: [255, 0, 128],
    1: [255, 0, 0],
    11: [0, 255, 255]
}


def get_bands():
    band = bands.Bands(**fixture)
    print(band.values)
