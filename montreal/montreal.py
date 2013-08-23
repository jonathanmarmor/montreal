import sys
import datetime
import random
import math
from itertools import combinations

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.stream import Stream, Measure, Part, Score, Opus
from music21.meter import TimeSignature
from music21.duration import Duration
from music21.spanner import Glissando, Slur
from music21.metadata import Metadata
from music21.instrument import (Piccolo, SopranoSaxophone, Viola, Violoncello,
    Trombone, ElectricGuitar)
from music21.layout import StaffGroup
from music21.tempo import MetronomeMark

from utils import GOLDEN_MEAN, scale, frange
import movement_1
import movement_2


class Instruments(object):
    def __init__(self):
        self.names = ['fl', 'sax', 'vla', 'vc', 'tbn', 'gtr']
        self.fl = fl =Piccolo()
        self.sax = sax = SopranoSaxophone()
        self.vla = vla = Viola()
        self.vc = vc =Violoncello()
        self.tbn = tbn = Trombone()
        self.gtr = gtr = ElectricGuitar()
        self.l = [fl, sax, vla, vc, tbn, gtr]
        self.d = {}
        for name, inst in zip(self.names, self.l):
            inst.nickname = name
            self.d[name] = inst

        # lowest, highest notes
        ranges = [
            ('D5', 'C7'),  # Piccolo
            ('C4', 'C6'),  # Soprano Sax
            ('C3', 'E5'),  # Viola
            ('C2', 'E4'),  # Cello
            ('E2', 'B-4'),  # Trombone
            ('E2', 'A5')  # Guitar
        ]
        for r, i in zip(ranges, self.l):
            i.lowest_note = Pitch(r[0])
            i.highest_note = Pitch(r[1])
            i.all_notes = list(frange(i.lowest_note.ps, i.highest_note.ps + 1))
            i.all_notes_24 = list(frange(i.lowest_note.ps, i.highest_note.ps + 1, 0.5))

        self.piece_range = list(frange(Pitch('E2').ps, Pitch('C7').ps + 1))
        self.piece_range_at_least_two_instruments = list(frange(Pitch('E2').ps, Pitch('C6').ps + 1))

    def shared_notes(self, instruments):
        def f(a, b):
            return set(a).intersection(set(b))
        instrument_notes = [i.all_notes for i in instruments]
        if len(instrument_notes) == 0:
            return []
        result = reduce(f, instrument_notes)
        result = list(result)
        result.sort()
        return result

    def get_others_with_shared_notes(self, i):
        if type(i) is str:
            i = self.d[i]
        others = [self.d[n] for n in self.names if n != i.nickname]
        combos = [[i, other] for other in others]
        result = []
        for combo in combos:
            shared = self.shared_notes(combo)
            len_shared = len(shared)
            if len_shared:
                result.append((combo[-1], shared))
        return result

    def get_unison_ensembles(self, min_notes=1):
        self.unison_ensembles = {}
        for n in range(2, len(self.l)):
            for combo in combinations(self.l, n):
                shared = self.shared_notes(combo)
                if len(shared) >= min_notes:
                    combo_hash = ' '.join(sorted(list([i.nickname for i in combo])))
                    self.unison_ensembles[combo_hash] = {
                        'instruments': combo,
                        'notes': shared
                    }
        return self.unison_ensembles

    def who_can_play(self, ps):
        who = []
        for i in self.l:
            if ps in i.all_notes:
                who.append(i.nickname)
        return who


class Parts(object):
    def __init__(self, instruments):
        self.names = ['fl', 'sax', 'vla', 'vc', 'tbn', 'gtr']
        self.fl = fl = Part()
        self.sax = sax = Part()
        self.vla = vla = Part()
        self.vc = vc = Part()
        self.tbn = tbn = Part()
        self.gtr = gtr = Part()
        self.l = [fl, sax, vla, vc, tbn, gtr]
        self.d = {}
        for name, part, inst in zip(self.names, self.l, instruments.l):
            part.id = name
            self.d[name] = part
            part.insert(0, inst)


class Piece(object):
    def __init__(self, ranges=False):
        if ranges:
            # Don't make a piece, just show the instrument ranges
            self.make_score()
            for inst, part in zip(self.instruments.l, self.parts.l):
                measure = Measure()
                measure.timeSignature = TimeSignature('4/4')
                low = Note(inst.lowest_note)
                measure.append(low)
                high = Note(inst.highest_note)
                measure.append(high)
                part.append(measure)
        else:
            # Make the piece
            self.make_score()
            self.choose_piece_duration()
            self.make_movements()
            self.choose_when_quarter_tones_start()
            self.fix_rhythm_notation()

    def show(self):
        self.score.show()

    def make_score(self):
        score = self.score = Score()
        self.instruments = self.i = Instruments()
        self.parts = Parts(self.i)

        timestamp = datetime.datetime.utcnow()
        score.insert(0, self.get_metadata(timestamp))

        [score.insert(0, part) for part in self.parts.l]
        score.insert(0, StaffGroup(self.parts.l))

        score.insert(0, MetronomeMark(number=120))

        return score

    def get_metadata(self, timestamp, movement_number=None, movement_name=None):
        md = Metadata()
        md.title = 'Penguin Atlas of African History'
        md.composer = 'Jonathan Marmor'
        md.date = timestamp.strftime('%Y/%m/%d')
        md.groupTitle = 'Dedalus'
        md.dedication = 'Didier Aschour'
        if movement_number:
            md.movementNumber = movement_number
        if movement_name:
            md.movementName = movement_name
        return md

    def choose_piece_duration(self):
        """Choose the total number of beats in the piece

        Units are quarter notes at 120 beats per minute.
        Range is between 7.5 and a little more than 9 minutes.
        """
        self.piece_duration = random.randint(900, 1100)

    def make_movements(self):
        one, two = self.choose_movement_durations()
        self.movement_1 = movement_1.Movement1(one, self)
        self.movement_2 = movement_2.Movement2(two, self)

    def choose_movement_durations(self):
        """Choose the durations of the two major sections of the piece.

        Choose a split point between the golden mean of the whole piece and
        the golden mean of the section between the golden mean of the piece and
        the end of the piece."""

        minimum = GOLDEN_MEAN

        # The golden mean of the section between the golden mean and 1
        maximum = scale(minimum, 0, 1, minimum, 1)

        # Pick a random float between minimum and maximum
        division = scale(random.random(), 0, 1, minimum, maximum)

        # Get the durations of each section
        one = int(scale(division, 0, 1, 0, self.piece_duration))
        two = self.piece_duration - one
        return one, two

    def choose_when_quarter_tones_start(self):
        # somewhere between 2 and 4 minutes in
        # in quarter notes at 120 beats per minute (ie, half seconds)
        self.quarter_tones_start = scale(random.random(), 0, 1, 120 * 2, 120 * 4)

    def fix_rhythm_notation(self):
        for part in self.parts.l:
            part.makeBeams()


if __name__ == '__main__':
    print 'STARTING!!!', '*' * 40
    show = True
    if 'ranges' in sys.argv:
        piece = Piece(ranges=True)
    else:
        piece = Piece()

    if 'noshow' not in sys.argv:
        piece.show()
