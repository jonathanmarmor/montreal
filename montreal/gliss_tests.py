import sys

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.stream import Stream, Measure, Part, Score, Opus
from music21.meter import TimeSignature, MeterSequence, MeterTerminal
from music21.duration import Duration
from music21.spanner import Glissando, Slur, Line
from music21.metadata import Metadata
from music21.instrument import (Piccolo, SopranoSaxophone, Viola, Violoncello,
    Trombone, ElectricGuitar)
from music21.layout import StaffGroup



def slur_test():
    stream = Stream()

    n1 = Note('C4')
    n2 = Note('D4')

    slur = Slur([n1, n2])

    stream.append([n1, n2])
    stream.insert(0, slur)

    stream.show()


def gliss_test():
    stream = Stream()

    n1 = Note('C4')
    n2 = Note('D4')
    n3 = Note('E4')
    n4 = Note('F4')
    n5 = Note('G4')
    n6 = Note('A4')

    gliss1 = Glissando([n2, n3])

    gliss2 = Glissando()
    gliss2.addSpannedElements([n5, n6])

    stream.append([n1, n2, n3, n4, n5, n6])
    stream.insert(0, gliss1)
    stream.insert(0, gliss2)

    stream.show()


def line_test():
    stream = Stream()

    line_types = ['solid', 'dashed', 'dotted', 'wavy']

    line = Line()
    line.lineType = 'solid'
    # line.startHeight
    # line.endHeight

    # line.startTick
    # line.endTick

    n1 = Note('C4')
    n2 = Note('D4')
    # n3 = Note('E4')
    # n4 = Note('F4')
    # n5 = Note('G4')
    # n6 = Note('A4')

    line.addSpannedElements([n1, n2])

    stream.append([n1, n2])
    stream.insert(0, line)

    stream.show()


def main():
    slur_test()


if __name__ == '__main__':
    main()