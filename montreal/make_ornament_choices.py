#! /usr/bin/env python

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

        if abs(a - b) > 4:
            return False

    return True


def make_orn_types():
    orn_types = defaultdict(lambda: defaultdict(list))
    for n in range(1, 5):
        for comb in itertools.product(range(-4, 5), repeat=n):

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

# This is broken
# def write(orn_types):
#     string = []
#     string.append('orn_types = {')
#     for n in range(1, 5):
#         string.append('\t{}: {{'.format(n))
#         for direction in ['ascending', 'descending']:

#             string.append('\t\t{}: S('.format(direction))

#             string.append('\t\t\t(75, S(')
#             string.append('\t\t\t')
#             string.append('\t\t\t),')

#             string.append('\t\t\t(20, S(')
#             for orn in orn_types[n][direction]:
#                 string.append('\t\t\t\t(50, {}),'.format(orn))
#             string.append('\t\t\t),')

#             string.append('\t\t\t(5, S(')
#             string.append('\t\t\t')
#             string.append('\t\t\t),')

#             string.append('\t\t},')

#         string.append('\t},')
#     string.append('}')
#     return '\n'.join(string)


def main():
    orn_types = make_orn_types()
    string = write(orn_types)
    print string


if __name__ == '__main__':
    main()



