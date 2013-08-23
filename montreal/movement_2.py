import random
from collections import defaultdict

from music21.stream import Measure
from music21.meter import TimeSignature
from music21.duration import Duration
from music21.note import Note, Rest
from music21.pitch import Pitch

from utils import fill, count_intervals, subdivide


class Phrase(object):
    def __init__(self, n, piece, movement, quadlet, couplet, lines):
        self.n = n
        self.piece = piece
        self.movement = movement
        self.quadlet = quadlet
        self.couplet = couplet
        self.lines = lines
        self.duration = quadlet.phrase_duration

        self.first = False
        if n == 1 and couplet.n == 1:
            self.first = True

        for line in lines:
            # print ('.' * int(line['rhythm'][0] * 2)) + ('-' * int(line['rhythm'][1] * 2)) + ('.' * int(line['rhythm'][2] * 2))
            part = piece.parts.d[line['instrument']]

            measure = Measure()
            if self.first and quadlet.previous_phrase_duration != self.duration:
                ts = TimeSignature('{}/4'.format(self.duration), self.duration)

                # ts.beatSequence.subdivideNestedHierarchy(3)

                # ts.beatSequence.partitionByList(subdivide(self.duration, 4))
                # for i, b in enumerate(ts.beatSequence):
                #     if b.duration.quarterLength == 4:
                #         ts.beatSequence[i] = b.subdivide(2)
                #         # ts.beatSequence[i][0] = b.subdivide(2)
                #         # ts.beatSequence[i][1] = b.subdivide(2)
                #     elif b.duration.quarterLength == 3:
                #         ts.beatSequence[i] = b.subdivideByList([2, 1])
                #         # ts.beatSequence[i][0] = ts.beatSequence[i].subdivide(2)
                #     elif b.duration.quarterLength == 2:
                #         ts.beatSequence[i] = b.subdivide(2)
                measure.timeSignature = ts

            r1_dur, note_dur, r2_dur = line['rhythm']

            if r1_dur > 0:
                r1 = Rest()
                r1.duration = Duration(r1_dur)
                measure.append(r1)

            p = Pitch(line['pitch'])
            # Force all flats
            if p.accidental.name == 'sharp':
                p = p.getEnharmonic()

            note = Note(p)
            note.duration = Duration(note_dur)
            measure.append(note)

            if r2_dur > 0:
                r2 = Rest()
                r2.duration = Duration(r2_dur)
                measure.append(r2)

            # fixed_measure = measure.sliceByBeat()
            # part.append(fixed_measure)

            part.append(measure)

        # Put full measure rests in instruments that aren't playing
        playing = [line['instrument'] for line in lines]
        resting = [i for i in piece.instruments.names if i not in playing]

        for i in resting:
            # print '.' * self.duration * 2
            part = piece.parts.d[i]

            measure = Measure()
            if self.first and quadlet.previous_phrase_duration != self.duration:
                ts = TimeSignature('{}/4'.format(self.duration), self.duration)

                # ts.beatSequence.subdivideNestedHierarchy(3)

                # ts.beatSequence.partitionByList(subdivide(self.duration, 4))
                # for i, b in enumerate(ts.beatSequence):
                #     if b.duration.quarterLength == 4:
                #         ts.beatSequence[i] = b.subdivide(2)
                #         # ts.beatSequence[i][0] = b.subdivide(2)
                #         # ts.beatSequence[i][1] = b.subdivide(2)
                #     elif b.duration.quarterLength == 3:
                #         ts.beatSequence[i] = b.subdivideByList([2, 1])
                #         # ts.beatSequence[i][0] = ts.beatSequence[i].subdivide(2)
                #     elif b.duration.quarterLength == 2:
                #         ts.beatSequence[i] = b.subdivide(2)
                measure.timeSignature = ts

            r = Rest()
            r.duration = Duration(self.duration)
            measure.append(r)

            # fixed_measure = measure.sliceByBeat()
            # part.append(fixed_measure)

            part.append(measure)


class Couplet(object):
    def __init__(self, n, piece, movement, quadlet, lines):
        self.n = n
        self.piece = piece
        self.movement = movement
        self.quadlet = quadlet
        self.lines = lines
        self.duration = quadlet.phrase_duration * 2

        self.phrase_a = Phrase(1, piece, movement, quadlet, self, lines)
        self.phrase_b = Phrase(2, piece, movement, quadlet, self, lines)


class Quadlet(object):
    def __init__(self, piece, movement):
        self.piece = piece
        self.movement = movement

        # in quarter notes at 120 bpm
        self.phrase_duration = random.randint(4, 9)
        if movement.quadlets:
            self.previous_phrase_duration = movement.quadlets[-1].phrase_duration
        else:
            self.previous_phrase_duration = None

        # Multiply by 4 because the quadlet repeats the phrase 4 times
        self.duration = self.phrase_duration * 4

        opts_a = piece.i.names[:]
        opts_b = piece.i.names[:]

        min_resting = random.choice([0, 1, 2, 3])
        self.lines = []
        while len(opts_a) > min_resting and len(opts_b) > min_resting:
            a = random.choice(opts_a)
            others = piece.i.get_others_with_shared_notes(a)
            others = [o for o in others if o[0].nickname in opts_b]
            if len(others) == 0:
                break
            inst_b, notes = random.choice(others)
            b = inst_b.nickname
            rhythm = self.choose_rhythm(self.phrase_duration)

            # print ('.' * int(rhythm[0] * 2)) + ('-' * int(rhythm[1] * 2)) + ('.' * int(rhythm[2] * 2))

            self.lines.append({
                'instrument_a': a,
                'instrument_b': b,
                'note_opts': notes,
                'rhythm': rhythm
            })
            opts_a.remove(a)
            opts_b.remove(b)

        self.choose_pitches(self.lines)

        couplet_a_lines = []
        couplet_b_lines = []

        for line in self.lines:
            couplet_a_lines.append({
                'instrument': line['instrument_a'],
                'pitch': line['pitch'],
                'rhythm': line['rhythm']
            })
            couplet_b_lines.append({
                'instrument': line['instrument_b'],
                'pitch': line['pitch'],
                'rhythm': line['rhythm']
            })
        self.couplet_a = Couplet(1, piece, movement, self, couplet_a_lines)
        self.couplet_b = Couplet(2, piece, movement, self, couplet_b_lines)

    def choose_rhythm(self, dur_to_fill):
        durs = fill(dur_to_fill * 2)
        durs = [d / 2.0 for d in durs]
        return durs

    def get_harmonies(self, lines):
        beat_map = defaultdict(list)
        for line in lines:
            r1, n, r2 = line['rhythm']
            r1 = int(r1 * 2)
            n = int(n * 2)

            for beat in range(n):
                beat = beat + r1
                beat_map[beat].append(line)

        harmonies = []
        for beat in beat_map:
            harmony = []
            for line in beat_map[beat]:
                harmony.append(line.get('pitch'))
            harmonies.append(harmony)
        return harmonies

    def validate_harmony(self, harmony):
        harmony = list(set([int(p % 12) for p in harmony]))
        harmony.sort()
        lowest = min(harmony)
        harmony = [p - lowest for p in harmony]

        interval_count = count_intervals(harmony)
        intervals = interval_count.keys()
        if set([1, 6, 11]).intersection(intervals):
            return False

        if harmony == [0, 4, 8]:
            return False

        return True

    def choose_pitches(self, lines):
        for line in lines:
            line['pitch'] = random.choice(line['note_opts'])

        harmonies = self.get_harmonies(lines)
        valid = all([self.validate_harmony(h) for h in harmonies])
        if not valid:
            self.choose_pitches(lines)


class Movement2(object):
    def __init__(self, duration, piece):
        self.duration = duration
        self.quadlets = []

        total = 0
        while total < duration:
            quadlet = Quadlet(piece, self)
            self.quadlets.append(quadlet)
            total += quadlet.duration
