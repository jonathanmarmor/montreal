from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.stream import Stream, Measure, Part, Score, Opus
from music21.meter import TimeSignature, MeterSequence, MeterTerminal
from music21.duration import Duration
from music21.spanner import Glissando, Slur
from music21.metadata import Metadata
from music21.instrument import (Piccolo, SopranoSaxophone, Viola, Violoncello,
    Trombone, ElectricGuitar)
from music21.layout import StaffGroup

"""
Rhythm notation criteria
-



"""

def bar1():
    notes = []
    # Eighth rest, eighth tied to half tied to eighth, eighth rest
    r1 = Rest()
    r1.duration = Duration(0.5)
    notes.append(r1)

    n1 = Note()
    n1.duration = Duration(3.0)
    notes.append(n1)

    r2 = Rest()
    r2.duration = Duration(0.5)
    notes.append(r2)
    return notes


def notate_measure(notes):
    ts = TimeSignature('4/4')
    ts.beatSequence.partition(4)
    print ts.beatSequence

    ts.beamSequence.partition(4)
    print ts.beamSequence




    # ts.beatSequence[0] = ts.beatSequence[0].subdivide(['1/2', '1/2'])


    # ts.beatSequence[0] = ts.beatSequence[0].subdivide(2)
    # ts.beatSequence[1] = ts.beatSequence[1].subdivide(2)

    m = Measure()
    m.timeSignature = ts
    [m.append(n) for n in notes]

    m.sliceByBeat(inPlace=True)
    return m


if __name__ == '__main__':
    score = Score()
    bars = [bar1]
    for bar in bars:
        notes = bar()
        measure = notate_measure(notes)
        score.append(measure)
    score.show()
