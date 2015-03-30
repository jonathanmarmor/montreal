import random
from itertools import combinations, groupby
import itertools
from collections import Counter, defaultdict


def scale(x, minimum, maximum, floor=0, ceiling=1):
    return ((ceiling - floor) * (float(x) - minimum))/(maximum - minimum) + floor


def scale_list(l, floor=0, ceiling=1):
    minimum = 0
    maximum = sum(l)
    return [scale(x, minimum, maximum, floor, ceiling) for x in l]


def weighted_choice(options, weights):
    rand = random.random()
    rand = scale(rand, 0, 1, 0, sum(weights))
    total = 0
    for i, weight in enumerate(weights):
        total += weight
        if rand < total:
            return options[i]


def fibonacci(n):
    a, b = 0, 1
    for x in range(n):
        a, b = b, a + b
    return a


GOLDEN_MEAN = float(fibonacci(30)) / fibonacci(31)


def divide(dur, units):
    """Divide the length `dur` into `units` sections"""
    if units > dur:
        return "hey, you can't divide `dur` into a number of units greater than `dur`"
    divs = []
    while len(divs) < units - 1:
        r = random.randint(1, dur - 1)
        if r not in divs:
            divs.append(r)
    divs.sort()
    divs.append(dur)
    result = []
    prev = 0
    for d in divs:
        unit = d - prev
        result.append(unit)
        prev = d
    return result


def fill(dur, min_note_dur=1):
    """put a single duration within a larger duration with a rest at the beggining, end, or both"""
    note_dur = random.randint(1, dur - 1)
    start = random.randint(0, dur - note_dur)
    rest_1_dur = start
    rest_2_dur = dur - (start + note_dur)
    return rest_1_dur, note_dur, rest_2_dur


def frange(x, y, step=1.0):
    while x < y:
        yield x
        x += step


def random_split(items):
    len_items = len(items)
    len_a = random.randint(1, len_items - 1)
    len_b = len_items - len_a
    a = random.sample(items, len_a)
    for item in a:
        items.remove(item)
    b = random.sample(items, len_b)
    return a, b


def count_intervals(harmony):
    counter = Counter()
    harmony += [12]
    for a, b in combinations(harmony, 2):
        counter[b - a] += 1
    del counter[12]
    return counter


def subdivide(n, biggest=4):
    """Break down `n` into as many units the size of `biggest` as possible then tack on the remainder"""
    result = []
    bigs = int(n) / biggest
    for r in range(bigs):
        result.append(biggest)
    remainder = n % biggest
    if remainder:
        result.append(remainder)
    return result


def split_at_offsets(dur, offsets):
    """split a single duration at offsets."""
    if len(offsets) == 0:
        return [dur]

    components = []
    offsets.append(dur)
    start = 0
    for offset in offsets:
        components.append(offset - start)
        start = offset

    return components


def split_at_beats(note_durs):
    """Split a list of durations at quarter notes."""
    beat_indexes = list(frange(0, sum(note_durs)))

    total = 0
    components = []
    for dur in note_durs:
        start = total
        end = total + dur

        split_at = []
        for beat in beat_indexes:
            if start < beat < end:
                split_point = beat - start
                split_at.append(split_point)

        note_components = split_at_offsets(dur, split_at)
        components.append(note_components)
        total += dur

    return components


def join_quarters(dur_components):
    """For duration components of a single note, join together any adjacent quarter note components"""
    new_durs = []
    for key, group in groupby(dur_components):
        new_dur = key
        len_group = len(list(group))
        if key == 1.0 and len_group > 1:
            new_dur = float(len_group)
        new_durs.append(new_dur)
    return new_durs


def get_inversions(chord):
    inversions = []
    for p1 in chord:
        inversion = [(p2 - p1) % 12 for p2 in chord]
        inversion.sort()
        inversions.append(tuple(inversion))
    return inversions


class S(object):
    def __init__(self, *args, **kwargs):
        if 'arguments' in kwargs:
            args = kwargs['arguments']
        self.weighted_options = args

    def choose(self):
        weights, options = zip(*self.weighted_options)
        choice = weighted_choice(options, weights)
        if isinstance(choice, S):
            return choice.choose()
        return choice


def set_start_end(notes):
    offset = 0
    for note in notes:
        note['start'] = offset
        note['end'] = offset + note['duration']
        offset += note['duration']


def get_at(offset, notes):
    for note in notes:
        if note['start'] <= offset < note['end']:
            return note


def get_simul(lists_of_notes):
    """
    lists_of_notes must be a list of lists of dictionaries with duration and pitch attributes
    """
    for part in lists_of_notes:
        offset = 0
        for note in part:
            note['start'] = offset
            note['end'] = offset + note['duration']
            offset += note['duration']

    beat_map = defaultdict(list)
    duration = sum([note['duration'] for note in lists_of_notes[0]])
    for offset in frange(0, duration, .25):
        for part in lists_of_notes:
            for note in part:
                if note['start'] <= offset < note['end']:
                    beat_map[offset].append(note)

    simuls = []
    for beat in frange(0, duration, .25):
        simul = []
        for note in beat_map[beat]:
            pitch = note['pitch']
            if not isinstance(pitch, list):
                pitch = [pitch]
            for p in pitch:
                if p not in simul:
                    simul.append(p)
        simuls.append(simul)
    return simuls






    beat_map = defaultdict(list)
    for part in lists_of_notes:
        beat = 0
        for note in part:
            dur = note['duration']
            for b in frange(0, dur, .25):
                if note['pitch'] != 'rest':
                    beat_map[beat].append(note)
                beat += .25

    print beat_map

    simuls = []
    for beat in beat_map:
        simul = []
        for note in beat_map[beat]:
            pitch = note['pitch']
            if not isinstance(pitch, list):
                pitch = [pitch]
            for p in pitch:
                if p not in simul:
                    simul.append(p)
        simuls.append(simul)
    return simuls


def midi_note_number_to_scientific_name(number):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave, name_index = divmod(number, 12)
    octave = octave - 1
    name = names[name_index]
    return '{}{}'.format(name, octave)


def get_by_attr(items, key, value):
    return next((item for item in items if item.get(key) == value), None)


def exp_weights(n, exponent=2, reverse=True):
    weights = [(x + 1) ** exponent for x in range(n)]
    weights.reverse()
    return weights


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2,s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)
