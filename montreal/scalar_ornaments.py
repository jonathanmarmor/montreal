import random

import itertools
from collections import defaultdict


def pairwise(iterable):
    """
    >>> list(pairwise(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def is_good(ornament):
    # Get rid of repeated notes
    if ornament[-1] == 0:
        return False

    pairs = pairwise(ornament)

    for a, b in pairs:
        if a == b:
            return False

        if abs(a - b) > 3:
            return False

    return True


def make_orn_types():
    orn_types = defaultdict(lambda: defaultdict(list))
    for n in range(1, 7):
        for comb in itertools.product(range(-2, 3), repeat=n):

            if not is_good(comb):
                continue

            sum_comb = sum(comb)
            if sum_comb <= 0:
                direction = 'ascending'
                orn_types[n][direction].append(comb)

            if sum_comb >= 0:
                direction = 'descending'
                orn_types[n][direction].append(comb)
    return orn_types


orn_types = make_orn_types()


def choose(n, direction):
    return random.choice(orn_types[n][direction])
