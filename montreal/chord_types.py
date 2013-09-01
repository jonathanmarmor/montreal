import random

from utils import weighted_choice, count_intervals, scale
import context_free_harmony


def validate_harmony(harmony):
    harmony = harmony[:]
    interval_count = count_intervals(harmony)
    intervals = interval_count.keys()
    if set([1, 6, 11]).intersection(intervals):
        return False
    if tuple(harmony[:-1]) in context_free_harmony.chord_types:
        return False
    return True


def get_random_harmony():
    num_notes = random.randint(2, 7)
    harmony = random.sample(range(12), num_notes)
    harmony.sort()
    lowest = min(harmony)
    harmony = [p - lowest for p in harmony]
    if not validate_harmony(harmony):
        return get_random_harmony()
    return tuple(harmony)


def get_random_valids():
    number = random.randint(4, 10)
    harmonies = []
    while len(harmonies) < number:
        harmony = get_random_harmony()
        if harmony not in harmonies:
            harmonies.append(harmony)
    return harmonies


def get_harmony_generator():
    extra_harmonies = get_random_valids()

    if random.random < .3:
        # fewer extra harmonies
        percent_extra = scale(random.random(), 0, 1, 0.0, 0.1)

    else:
        # more extra harmonies
        percent_extra = scale(random.random(), 0, 1, 0.1, 0.6)

    while True:
        if random.random() < percent_extra:
            yield random.choice(extra_harmonies)
        else:
            yield context_free_harmony.choose()
