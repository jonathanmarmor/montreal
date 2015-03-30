import random
import itertools
from collections import defaultdict

from utils import weighted_choice, exp_weights


def rank_by_distance(previous, options):
    distance_preferences = [0, 2, 1, 3, 4, 5, 7, 6]
    distances = [abs(previous - p) for p in options]
    ranked = sorted(zip(distances, options), key=lambda x: distance_preferences.index(x[0]))

    # Shuffle rank of pitches that have the same distance
    distance_groups = itertools.groupby(ranked, key=lambda x: x[0])
    new_ranks = []
    for distance, group in distance_groups:
        group = list(group)
        random.shuffle(group)
        new_ranks.extend(group)

    return [item[1] for item in new_ranks]


def next_simple_accompaniment_note(previous, harmony, lowest_pitch, highest_pitch):
    harmony = [p % 12 for p in harmony]
    options = [p for p in range(previous - 7, previous + 8) if p % 12 in harmony and p >= lowest_pitch and p <= highest_pitch]
    ranked_by_distance = rank_by_distance(previous, options)

    ranks = defaultdict(list)
    len_options = len(options)
    for p in options:
        rank = len_options - ranked_by_distance.index(p)
        ranks[rank].append(p)
    ranked = []
    for k in sorted(ranks.keys(), reverse=True):
        random.shuffle(ranks[k])
        ranked.extend(ranks[k])

    weights = exp_weights(len(ranked))
    return weighted_choice(ranked, weights)
