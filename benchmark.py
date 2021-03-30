from time import time, sleep

import numpy as np


def benchmark(fx, fps):
    print('You enabled the benchmark flag, time to measure performance!')
    print('The script will run for a specified amount of cycles, then')
    print('present the results and exit. More cycles take longer to finish.')
    print('Please specify the amount of cycles now (defaults to 200).')
    print('---------------------------------------------------')

    cycle_choice = input()
    cycle = 0

    data = []

    try:
        cycles = int(cycle_choice)
    except ValueError:
        cycles = 200

    quarter = cycles / 4
    quarter_passed = False

    half = cycles / 2
    half_passed = False

    three_quarter = quarter + half
    three_quarter_passed = False

    def timer():
        start = time()
        fx.loop()
        elapsed = (time() - start) * 1000
        data.append(elapsed)
        sleep(1 / fps)

    print('Lets go!')
    while cycle < cycles:
        if cycle > quarter and not quarter_passed:
            print('25 percent, let\'s keep going!')
            quarter_passed = True
        if cycle > half and not half_passed:
            print('halfway there already!')
            half_passed = True
        if cycle > three_quarter and not three_quarter_passed:
            print('Almost there, hold on!')
            three_quarter_passed = True

        timer()
        cycle += 1

    result = np.asarray(data)
    print('Benchmark complete!')
    print('---------------------------------------------------')
    print('On average, a cycle took %s ms.' % result.mean().round(decimals=2))
    print('The longest cycle took %(longest)s ms, the shortest %(shortest)s ms.' % {
        'longest': result.max().round(decimals=2),
        'shortest': result.min().round(decimals=2),
    })
