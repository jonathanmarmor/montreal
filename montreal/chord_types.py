import random

from utils import weighted_choice


# See Animal Play chord_types.py for how this list was generated
other_harmonies = [
    (0, 3, 10),
    (0, 2, 7, 9),
    (0, 2, 5, 7, 9),
    (0, 2, 7, 10),
    (0, 3, 5, 7, 10),
    (0, 2, 5, 10),
    (0, 2, 4, 7, 9),
    (0, 7, 10),
    (0, 2, 5, 7, 10),
    (0, 2, 4, 9),
    (0, 7, 9),
    (0, 3, 8, 10),
    (0, 4, 8),
    (0, 2, 4),
    (0, 3, 5, 8, 10),
    (0, 3, 5, 7),
    (0, 2, 5),
    (0, 5, 8, 10),
    (0, 2, 4, 7),
    (0, 5, 7, 10),
    (0, 8, 10),
    (0, 5, 7, 9),
    (0, 2, 9),
    (0, 2, 5, 7),
    (0, 3, 5),
    (0, 2, 10),
    (0, 3, 5, 10)
]


def choose_primary():
    options = [
        (0, 4, 7),
        (0, 3, 7),
        (0, 4, 7, 10),
        (0, 3, 7, 10),
        (0, 7),
        (0, 4, 7, 11),
        (0, 5, 7),
        (0, 5),
        (0, 4),
    ]
    weights = [
        47,
        19,
        15,
        7,
        6,
        2,
        2,
        1,
        1,
    ]
    return weighted_choice(options, weights)


def get_chord_type():
    if random.random() < .1:
        return random.choice(other_harmonies)
    else:
        return choose_primary()
