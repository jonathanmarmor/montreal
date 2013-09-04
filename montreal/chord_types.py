import random

from utils import weighted_choice, count_intervals, scale, get_inversions
import context_free_harmony


# CHORD_TYPES = []
# for chord in context_free_harmony.chord_types:
#     CHORD_TYPES.extend(get_inversions(chord))


# def validate_harmony(harmony):
#     harmony = harmony[:]
#     interval_count = count_intervals(harmony)
#     intervals = interval_count.keys()
#     if set([1, 6, 11]).intersection(intervals):
#         return False
#     if tuple(harmony[:-1]) in CHORD_TYPES:
#         return False
#     return True


# def get_random_harmony():
#     num_notes = random.randint(3, 5)
#     harmony = random.sample(range(12), num_notes)
#     harmony.sort()
#     lowest = min(harmony)
#     harmony = [p - lowest for p in harmony]
#     if not validate_harmony(harmony):
#         return get_random_harmony()
#     return tuple(harmony)


# The result of running get_random_harmony 10000 times:
OTHERS = [
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

def get_random_valids():
    number = random.randint(4, 7)
    harmonies = random.sample(OTHERS, number)
    # harmonies = []
    # while len(harmonies) < number:
    #     harmony = get_random_harmony()
    #     if harmony not in harmonies:
    #         harmonies.append(harmony)
    return harmonies


def get_harmony_generator():
    other_harmonies = get_random_valids()

    if random.random() < .7:
        # fewer other harmonies
        percent_other = scale(random.random(), 0, 1, 0.0, 0.1)

    else:
        # more other harmonies
        percent_other = scale(random.random(), 0, 1, 0.1, 0.6)

    while True:
        if random.random() < percent_other:
            yield random.choice(other_harmonies)
        else:
            yield context_free_harmony.choose()
