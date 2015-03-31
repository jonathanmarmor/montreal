import random

from utils import weighted_choice


def random_vibraphone_voicing(lowest, highest):
    # Voicing of the harmonic series
    prototype = [12, 19, 24, 28, 31, 34, 36, 38, 40, 42, 43, 44]
    offset = weighted_choice([0, 1, 2], [5, 4, 2])
    prototype = prototype[offset:]
    prototype = [p - prototype[0] for p in prototype]

    lowest = random.randint(lowest, lowest + 9)
    highest = random.randint(highest - 8, highest)

    options = [lowest + p for p in prototype if lowest + p < highest]

    len_options = len(options)

    if len_options < 5:
        return random_vibraphone_voicing(lowest, highest)

    if len_options >= 8:
        most = 8
    else:
        most = len_options
    n = random.randint(5, most)

    voicing = random.sample(options, n)
    voicing.sort()
    return voicing


def next_vibraphone_chord(previous, harmony, lowest, highest):
    options = [p for p in range(lowest, highest + 1) if p % 12 in harmony]

    previous_type = set([p % 12 for p in previous])
    if not set(harmony).intersection(previous_type):
        previous = random_vibraphone_voicing(lowest, highest)

    size_change = random.choice([-1, 0, +1])
    n = len(options) + size_change
    if n > 8: n = 8
    if n < 5: n = 5

    new = set()
    for p in previous:
        for trans in range(8):
            if p - trans in options:
                chosen = p - trans
                new.add(chosen)
                break
            elif p + trans in options:
                chosen = p + trans
                new.add(chosen)
                break

    # TODO This isn't great but it sounds ok so I'm leaving it.

    new = list(new)
    new.sort()
    return new
