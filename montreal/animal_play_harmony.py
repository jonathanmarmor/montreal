# -*- coding: utf-8 -*-

import itertools
from collections import Counter, defaultdict
import random

from utils import weighted_choice, pairwise, exp_weights


def partitions(n):
    """Get all the partitions of an integer n.

    From: http://homepages.ed.ac.uk/jkellehe/partitions.php

    >>> [part for part in partitions(4)]
    [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2], [4]]

    """
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2*x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield a[:k + 1]


def inversions(chord):
    """Get all inversions of a list of intervals.

    >>> [inv for inv in inversions((4, 3, 5))]
    [(4, 3, 5), (3, 5, 4), (5, 4, 3)]

    NOTE: for interval lists, not pitch classes.
    """
    chord = list(chord)
    for i, note in enumerate(chord):
        inverted = chord[i:] + chord[:i]
        yield tuple(inverted)


def get_chord_classes(max_notes=6):
    """Get all

    """
    chord_classes = set()
    for partition in partitions(12):
        len_partition = len(partition)
        if len_partition > 1 and len_partition <= max_notes:
            for perm in itertools.permutations(partition):
                # If no inversions of perm are in chord_classes, add perm
                if not any([inversion in chord_classes for inversion in inversions(perm)]):
                    chord_classes.add(perm)
    return chord_classes


def get_interval_content(chord):
    """Get counts of each interval appearing in a chord
    (m2, M2, m3, M3, P4, TT)

    >>> get_interval_content((4, 3, 5))
    (0, 0, 1, 1, 1, 0)

    >>> get_interval_content((4, 3, 3, 2))
    (0, 1, 2, 1, 1, 1)

    >>> get_interval_content((6, 6))
    (0, 0, 0, 0, 0, 1)


    """
    chord = list(chord)
    content = Counter()
    n_intervals = len(chord)
    for width in range(1, n_intervals):
        for i, n in enumerate(chord):
            if i + width < n_intervals:
                notes = chord[i:i + width]
            else:
                notes = chord[i:] + chord[:(i + width) % n_intervals]
            interval = sum(notes)
            if interval <= 6:
                content[interval] += 1
    if content[6] > 1:
        content[6] = content[6] / 2
    return tuple([content[i] for i in range(1, 7)])


def choose_next_harmony(history, chord_type):
    last = history[-1]
    intervals = pitches_to_intervals(chord_type)
    chords = build_chord_type_on_all_roots(intervals)

    scored = []
    for chord in chords:
        transition_score = score_transition(last, chord)
        scored.append({
            'chord': chord,
            'chord_type': chord_type,
            'transition_score': transition_score,
        })

    scored.sort(key=lambda x: x['transition_score'], reverse=True)

    options = scored[:6]
    weights = [10, 5, 3, 2, 1]
    choice = weighted_choice(options, weights)
    return choice['chord']


def score_transition(a, b):
    score = 0
    if a == b:
        return 0
    for ap, bp in itertools.product(a, b):
        interval = ap - bp
        interval = abs(interval)

        if interval > 6:
            interval = 12 - interval

        if interval == 0:
            score += 100
        elif interval == 1:
            score += 20
        elif interval == 2:
            score += 15
        elif interval == 5:
            score += 10

    len_b = len(b)

    score = score / len_b

    if len_b <= 3:
        score += 50

    return score





def score_chords():
    scored = []
    for chord in get_chord_classes():
        score = score_chord(chord)
        scored.append((chord, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)


def get_weighted_chords(more_dissonant=False):
    scored = score_chords()
    # filtering out everything below zero is just my choice from eyeballing the
    # options and deciding which harmonies I probably don't want to happen in
    # this piece.
    scored = [(chord, score) for chord, score in scored if score > 0]
    chords = [chord for chord, score in scored]
    len_chords = len(chords)
    if more_dissonant:
        a = [1.05**i for i in range(1, len_chords - 12)]
        b = [1.05**i for i in range(len_chords - 12, len_chords - 25, -1)]
        weights = a + b
    else:
        weights = [1.175**i for i in range(1, len(chords) + 1)]
    weights.reverse()
    return chords, weights


def build_chord_type_on_root(root, chord_type):
    """
    >>> build_chord_type_on_root(9, [4, 3, 5])
    [9, 1, 4]

    """
    chord = [root]
    for interval in chord_type[:-1]:
        chord.append((chord[-1] + interval) % 12)
    return chord


def build_chord_type_on_all_roots(chord_type):
    """
    >>> build_chord_type_on_all_roots([4, 3, 5])
    [[0, 4, 7],
     [1, 5, 8],
     [2, 6, 9],
     [3, 7, 10],
     [4, 8, 11],
     [5, 9, 0],
     [6, 10, 1],
     [7, 11, 2],
     [8, 0, 3],
     [9, 1, 4],
     [10, 2, 5],
     [11, 3, 6]]

    """
    return [build_chord_type_on_root(root, chord_type) for root in range(12)]


def intervals_to_pcs(root, chord):
    """
    >>> intervals_to_pcs(10, (4, 3, 5))
    (10, 2, 5)
    """
    n = root
    out = [n]
    for interval in chord[:-1]:
        n = (n + interval) % 12
        out.append(n)
    return tuple(out)


def pitches_to_intervals(chord):
    """
    >>> pitches_to_intervals([12, 16, 31])
    [4, 3, 5]
    """
    # TODO rewrite this
    pcs = sorted(list(set([p % 12 for p in chord])))
    pcs = [p - pcs[0] for p in pcs]
    pcs.reverse()
    pcs.insert(0, 12)
    intervals = []
    for a, b in pairwise(pcs):
        intervals.append(a - b)
    intervals.reverse()
    return intervals


def rotate(drone, chord):
    """return the chord built on the drone in all transpositions

    >>> rotate(10, (4, 3, 5))
    [(10, 2, 5), (10, 1, 6), (10, 3, 7)]
    """
    out = []
    for chord in inversions(chord):
        out.append(intervals_to_pcs(drone, chord))
    return out


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
    """return a list of the notes in the harmony in the order in which they are most likely to be used as the root.

    1. top of a P4
    2. bottom of a P4
    3. bottom of a M3
    5. top of a m3

    bottom of a m2 should be demoted.

    >>> ranked_roots([0, 4, 7])
    [0, 7, 4]

    >>> ranked_roots([0, 2, 4, 7, 11])
    [0, 4, 7, ]

    """

    weights = defaultdict(lambda: defaultdict(int))
    weights[5][1] = 200  # Top of P4
    weights[5][0] = 50  # Bottom of P4
    weights[4][0] = 20  # Bottom of M3
    weights[3][1] = 10  # Top of m3
    weights[4][1] = 9  # Top of M3
    weights[3][0] = 8  # Bottom of m3

    weights[6][0] = -1  # Bottom of tritone
    weights[6][1] = -1  # Top of tritone

    weights[1][0] = -100  # Bottom of m1

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


def choose_root(harmony):
    ranked = ranked_roots(harmony)
    weights = range(len(ranked), 0, -1)
    return weighted_choice(ranked, weights)


class Harmony(object):
    def __init__(self, drones):
        self.drones = drones
        self.CHORDS, self.WEIGHTS = get_weighted_chords()
        self.build_drone_chords()

    def choose(self, drone=None):
        if drone:
            return weighted_choice(self.DRONE_CHORDS[drone], self.DRONE_WEIGHTS[drone])
        chord_type = weighted_choice(self.CHORDS, self.WEIGHTS)
        root = random.choice(range(12))
        return build_chord_type_on_root(root, chord_type)

    def build_drone_chords(self):
        self.DRONE_CHORDS = defaultdict(list)
        self.DRONE_WEIGHTS = defaultdict(list)

        drones = []
        for drone in self.drones:
            if isinstance(drone, tuple):
                for p in drone:
                    drones.append(p)
            drones.append(drone)

        for drone in drones:
            for i, chord_type in enumerate(self.CHORDS):
                weight = self.WEIGHTS[i]
                # Build chord on all 12 roots
                chords = build_chord_type_on_all_roots(chord_type)
                for chord in chords:
                    if isinstance(drone, tuple):
                        # check each if it contains all pitches in drone
                        if all([pitch in chord for pitch in drone]):
                            self.DRONE_CHORDS[drone].append(chord)
                            self.DRONE_WEIGHTS[drone].append(weight)
                    else:
                        if drone in chord:
                            self.DRONE_CHORDS[drone].append(chord)
                            self.DRONE_WEIGHTS[drone].append(weight)
