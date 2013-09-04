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


def test():
    stream = Stream()

    n1 = Note('C4', duration=Duration(1.5))
    n2 = Note('D4', duration=Duration(0.5))
    n3 = Note('E4')
    n4 = Note('F4')
    n5 = Note('G4')
    n6 = Note('A4')

    n7 = Note('C4')
    n8 = Note('D4').getGrace()
    n9 = Note('E4').getGrace()
    n10 = Note('F4')
    n11 = Note('G4')
    n12 = Note('A4', duration=Duration(0.5))
    n13 = Note('A4', duration=Duration(0.5))

    gliss1 = Glissando([n2, n3])
    gliss2 = Glissando([n5, n6])
    gliss3 = Glissando([n6, n7])
    gliss4 = Glissando([n8, n9])

    slur1 = Slur([n2, n3])
    slur2 = Slur([n6, n7])
    slur3 = Slur([n9, n10])


    stream.append([n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13])
    stream.insert(0, gliss1)
    stream.insert(0, gliss2)
    stream.insert(0, gliss3)
    stream.insert(0, gliss4)
    stream.insert(0, slur1)
    stream.insert(0, slur2)
    stream.insert(0, slur3)

    return stream


if __name__ == '__main__':
    stream = test()

    if 'midi' in sys.argv:
        stream.show('midi')
    elif 'sib' in sys.argv:
        stream.show('musicxml', '/Applications/Sibelius 7.app')
    elif 'fin' in sys.argv:
        stream.show('musicxml', '/Applications/Finale 2012.app')
    else:
        stream.show('musicxml', '/Applications/MuseScore.app')

