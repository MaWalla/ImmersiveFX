from time import time

import numpy as np


def benchmark(fx):
    print('You enabled the benchmark flag, time to measure performance!')
    print('The script will run for a specified amount of cycles, then')
    print('present the results and exit. More cycles take longer to finish.')
    print('Please specify the amount of cycles now (defaults to 1000).')
    print('---------------------------------------------------')

    cycle_choice = input()
    cycle = 0

    data = []

    try:
        cycles = int(cycle_choice)
    except ValueError:
        cycles = 1000

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
    print(f'On average, a cycle took {result.mean()} ms.')
    print(f'The longest cycle took {result.max()} ms, the shortest {result.min()} ms.')