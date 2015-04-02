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


def is_in_scale(harmony, scale):
    return all([p in scale for p in harmony])


scale_types = {
    # 'diatonic': [0, 2, 4, 5, 7, 9, 11],
    'blues': [0, 3, 5, 6, 7, 10],
    'blues2': [0, 2, 3, 5, 6, 9, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'octatonic': [0, 2, 3, 5, 6, 8, 9, 11],
    'whole': [0, 2, 4, 6, 8, 10],
    'flat2_6': [0, 1, 4, 5, 7, 8, 11],
    'flat2_6_sharp4': [0, 1, 4, 6, 7, 8, 11],
}


def diatonic_scales_for_harmony(harmony):
    diatonic = [0, 2, 4, 5, 7, 9, 11]
    harmony = [p % 12 for p in harmony]
    scales = []
    for root in range(11):
        scale = [(p + root) % 12 for p in diatonic]
        if is_in_scale(harmony, scale):
            scale.sort()
            scales.append(scale)
    return scales


def other_scales_for_harmony(harmony):
    harmony = [p % 12 for p in harmony]
    scales = []
    for root in range(11):
        for scale_type in scale_types.values():
            scale = [(p + root) % 12 for p in scale_type]
            if is_in_scale(harmony, scale):
                scale.sort()
                scales.append(scale)
    return scales