from itertools import repeat
import random
import time
from random import getrandbits
from math import ceil
from multiprocessing import Pool, cpu_count

def original(n):
    """Small modification to add timing and additional logging"""
    start = time.time()
    items = [1,2,3,4]
    numbers = [0,0,0,0]
    rolls = 0
    maxOnes = 0

    while numbers[0] < 177 and rolls < n:
        numbers = [0,0,0,0]
        for i in repeat(None, 231):
            roll = random.choice(items)
            numbers[roll-1] = numbers[roll-1] + 1
        rolls = rolls + 1
        if numbers[0] > maxOnes:
            maxOnes = numbers[0]
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",rolls)
    print("%d rolls in %.1fs. %s rolls/s"%(rolls, end-start, rolls/(end-start)))
    return end-start, maxOnes, rolls

def improv_1(n):
    """Avoids indexing the list and only tracks how many "ones" were rolled"""
    start = time.time()
    maxOnes = 0
    for _ in range(n):
        ones=0
        for _ in range(231):
            if random.random()<=0.25:
                ones += 1
        maxOnes = max(maxOnes, ones)
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",n)
    print("%d rolls in %.1fs. %s rolls/s"%(n, end-start, n/(end-start)))
    return end-start, maxOnes, n


def improv_2(n):
    """From testing, itertools repeat was marginally faster than range"""
    start = time.time()
    maxOnes = 0
    for _ in repeat(None, n):
        ones=0
        for _ in repeat(None, 231):
            if random.random()<=0.25:
                ones += 1
        maxOnes = max(maxOnes, ones)
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",n)
    print("%d rolls in %.1fs. %s rolls/s"%(n, end-start, n/(end-start)))
    return end-start, maxOnes, n


def improv_3(n):
    """getrandbits(2) will produce a random number from 0-3 inclusive
    faster than randint(0,3) or checking random()<=0.25
    repeatedly resolving random.getrandbits is slow so avoid using
    from random import getrandbits"""
    start = time.time()
    maxOnes = 0
    for _ in repeat(None, n):
        ones=0
        for _ in repeat(None, 231):
            if not getrandbits(2):
                ones += 1
        if ones>maxOnes:
            maxOnes = ones
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",n)
    print("%d rolls in %.1fs. %s rolls/s"%(n, end-start, n/(end-start)))
    return end-start, maxOnes, n


def improv_3_m(n, p=None):
    """Using multiprocessing, cpu can be utilised more effectively
    This will do at least `n` rolls but may do more
    to make a multiple of the number of cores.
    Time reduction by this method will vary depending on cpu"""
    start = time.time()
    if p is None:
        p = cpu_count()
    per_core = ceil(n/p)
    with Pool(p) as pool:
        maxOnes = max(pool.map(_improv_m, repeat(per_core, p)))
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",per_core*p)
    print("%d rolls in %.1fs. %s rolls/s"%(per_core*p, end-start, per_core*p/(end-start)))
    return end-start, maxOnes, per_core*p


def improv_4_m(n, p=None):
    """imap_unordered showed marginal improvements over map"""
    start = time.time()
    if p is None:
        p = cpu_count()
    per_core = ceil(n/p)
    with Pool(p) as pool:
        maxOnes = max(pool.imap_unordered(_improv_m, repeat(per_core, p)))
    end = time.time()
    print("Highest Ones Roll:",maxOnes)
    print("Number of Roll Sessions: ",per_core*p)
    print("%d rolls in %.1fs. %s rolls/s"%(per_core*p, end-start, per_core*p/(end-start)))
    return end-start, maxOnes, per_core*p

def _improv_m(n):
    maxOnes = 0
    for _ in repeat(None, n):
        ones=0
        for _ in repeat(None, 231):
            if not getrandbits(2):
                ones += 1
        if ones>maxOnes:
            maxOnes = ones
    return maxOnes



if __name__ == '__main__':
    print("original:")
    original(500_000)
    print("improv_1:")
    improv_1(2_500_000)
    print("improv_2:")
    improv_2(2_500_000)
    print("improv_3:")
    improv_3(4_000_000)
    print("improv_4_m:")
    improv_4_m(100_000_000)

    print("original:")
    original(500_000)
    print("improv_1:")
    improv_1(500_000)
    print("improv_2:")
    improv_2(500_000)
    print("improv_3:")
    improv_3(500_000)
    print("improv_4_m:")
    improv_4_m(500_000)
    print("improv_4_m:")
    improv_4_m(1_000_000_000)
    """DATA:
    Testing was done on an Intel Xeon E5-2687W v4, 24 Core, 48 Processor, 3.00GHz CPU
    Roll numbers were chosen so each test would take about a minute.
    Rolls per second will be compared
    original:   500 000 rolls     took 71.4s (7 002 rolls/s)
    improv_1:   2 500 000 rolls   took 59.4s (42 063 rolls/s)
    improv_2:   2 500 000 rolls   took 59.1s (42 320 rolls/s)
    improv_3:   4 000 000 rolls   took 63.3s (63 175 rolls/s)
    improv_4_m: 100 000 032 rolls took 64.0s (1 563 317 rolls/s) (32 569 rolls/s/processor)

    All methods done on same number of rolls (500 000) for comparing times:
    original:    took 71.8s (6 961 rolls/s)
    improv_1:    took 12.2s (40 859 rolls/s)
    improv_2:    took 11.8s (42 312 rolls/s)
    improv_3:    took 7.7s  (64 762 rolls/s)
    improv_4_m*: took 0.8s  (645 186 rolls/s) (13 441 rolls/s/processor)
        *done for 500_016 rolls as the next multiple of 48 after 500 000

    improv_4_m done for 1 000 000 032 rolls:
        took 639.2s (1 564 572 rolls/s) (32 595 rolls/s/processor)
        Highest 1s roll: 100"""
