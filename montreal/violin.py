import random
import itertools
from collections import defaultdict

from utils import weighted_choice, exp_weights


def get_intervals(harmony):
    """
    >>> get_intervals([2, 6, 9])
    {
        3: [(6, 9)],
        4: [(2, 6)],
        5: [(9, 2)]
    }

    """
    intervals = defaultdict(list)
    for interval in range(1, 7):
        for bottom in harmony:
            top = (bottom + interval) % 12
            if top in harmony:
                intervals[interval].append((bottom, top))
    return dict(intervals)


def ranked_roots(harmony):
    """
    NOTE: This now ranks OPPOSITE of best root. To be used for choosing higher melody parts.

    return a list of the notes in the harmony in the order in which they are most likely to be used as the root.

    1. bottom of a P4
    2. top of a P4
    3. top of a M3
    5. bottom of a m3

    """

    weights = defaultdict(lambda: defaultdict(int))
    weights[5][0] = 45  # Bottom of P4
    weights[5][1] = 25  # Top of P4
    weights[4][1] = 15  # Top of M3
    weights[3][0] = 10  # Bottom of m3
    weights[4][0] = 9  # Bottom of M3
    weights[3][1] = 8  # Top of m3

    weights[6][1] = -1  # Top of tritone
    weights[6][0] = -1  # Bottom of tritone

    weights[1][1] = -1  # Top of m1

    weighted_notes = defaultdict(int)

    intervals = get_intervals(harmony)
    for size in intervals:
        for interval in intervals[size]:
            for i, p in enumerate(interval):
                weight = weights[size][i]
                weighted_notes[p] += weight
    items = weighted_notes.items()
    items = sorted(items, key=lambda x: x[1], reverse=True)

    # Shuffle rank of pitches with the same weights
    weight_groups = itertools.groupby(items, key=lambda x: x[1])
    ranked = []
    for weight, group in weight_groups:
        group = list(group)
        random.shuffle(group)
        ranked.extend(group)

    return [item[0] for item in ranked]


def rank_by_distance(previous, options):
    distance_preferences = [2, 1, 0, 3, 4, 5, 7, 6]
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


def rank_by_best_root(harmony, options):
    ranked = []
    roots = ranked_roots(harmony)
    for root in roots:
        pitches = [p for p in options if p % 12 == root]
        random.shuffle(pitches)
        ranked.extend(pitches)
    return ranked


def rank_options(previous, harmony, lowest_pitch, highest_pitch):
    options = [p for p in range(previous - 7, previous + 8) if p % 12 in harmony and p >= lowest_pitch and p <= highest_pitch]
    ranked_by_distance = rank_by_distance(previous, options)
    ranked_by_best_root = rank_by_best_root(harmony, options)

    ranks = defaultdict(list)
    len_options = len(options)
    for p in options:
        distance_rank = len_options - ranked_by_distance.index(p)
        root_rank = len_options - ranked_by_best_root.index(p)
        rank = distance_rank + root_rank
        ranks[rank].append(p)
    ranked = []
    for k in sorted(ranks.keys(), reverse=True):
        random.shuffle(ranks[k])
        ranked.extend(ranks[k])

    return ranked


def next_violin_dyad(previous, harmony, lowest_pitch, highest_pitch):
    harmony = [p % 12 for p in harmony]

    prev_lower = min(previous)
    prev_higher = max(previous)

    lower_ranked = rank_options(prev_lower, harmony, lowest_pitch, highest_pitch)
    higher_ranked = rank_options(prev_higher, harmony, lowest_pitch, highest_pitch)

    ranked = []
    for lower_rank, lower in enumerate(lower_ranked):
        for higher_rank, higher in enumerate(higher_ranked):
            interval = higher - lower
            if interval > 0 and interval < 8:
                rank = lower_rank + higher_rank
                ranked.append({
                    'rank': lower_rank + higher_rank,
                    'dyad': [lower, higher]
                })

    ranked.sort(key=lambda x: x['rank'])
    ranked = [r['dyad'] for r in ranked]

    weights = exp_weights(len(ranked))
    return weighted_choice(ranked, weights)
