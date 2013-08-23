import sys
import datetime
import random

from music21.note import Note
from music21.pitch import Pitch
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.instrument import Violin, Guitar
from music21.layout import StaffGroup
from music21.tempo import MetronomeMark

from utils import frange
import movement_1


class Instruments(object):
    def __init__(self):
        self.names = ['vln', 'gtr']
        self.vln = vln = Violin()
        self.gtr = gtr = Guitar()
        self.l = [vln, gtr]
        self.d = {}
        for name, inst in zip(self.names, self.l):
            inst.nickname = name
            self.d[name] = inst

        # lowest, highest notes
        ranges = [
            ('G3', 'B5'),  # Violin
            ('E2', 'G5')  # Guitar
        ]
        for r, i in zip(ranges, self.l):
            i.lowest_note = Pitch(r[0])
            i.highest_note = Pitch(r[1])
            i.all_notes = list(frange(i.lowest_note.ps, i.highest_note.ps + 1))
            i.all_notes_24 = list(frange(i.lowest_note.ps, i.highest_note.ps + 1, 0.5))


class Parts(object):
    def __init__(self, instruments):
        self.names = ['vln', 'gtr']
        self.vln = vln = Part()
        self.gtr = gtr = Part()
        self.l = [vln, gtr]
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
            self.make_movements()
            self.fix_rhythm_notation()

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
        md.title = 'Montreal'
        md.composer = 'Jonathan Marmor'
        md.date = timestamp.strftime('%Y/%m/%d')
        if movement_number:
            md.movementNumber = movement_number
        if movement_name:
            md.movementName = movement_name
        return md

    def make_movements(self):
        # 18 to 21 minutes
        piece_duration = random.randint(2160, 2520)
        self.movement_1 = movement_1.Movement1(piece_duration, self)

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

    if 'midi' in sys.argv:
        piece.score.show('midi')

    if 'noshow' not in sys.argv:
        piece.score.show()
