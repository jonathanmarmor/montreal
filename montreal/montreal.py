#!/usr/bin/env python

import sys
import datetime
import random

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.instrument import Violin, AcousticGuitar
from music21.layout import StaffGroup
from music21.tempo import MetronomeMark
from music21.duration import Duration

from utils import weighted_choice
from utils import count_intervals
from utils import frange
from utils import fill
from utils import divide
from utils import split_at_beats
from utils import join_quarters
from utils import scale
import harmonic_rhythm
import form
from chord_types import get_harmony_generator


class Instruments(object):
    def __init__(self):
        self.names = ['vln', 'gtr']
        self.vln = vln = Violin()
        self.gtr = gtr = AcousticGuitar()
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
            return

        score = self.score = Score()
        self.instruments = self.i = Instruments()
        self.parts = Parts(self.i)


        # Make Metadata
        timestamp = datetime.datetime.utcnow()
        metadata = Metadata()
        metadata.title = 'Montreal'
        metadata.composer = 'Jonathan Marmor'
        metadata.date = timestamp.strftime('%Y/%m/%d')
        score.insert(0, metadata)

        [score.insert(0, part) for part in self.parts.l]
        score.insert(0, StaffGroup(self.parts.l))





        # 18 to 21 minutes
        piece_duration_minutes = scale(random.random(), 0, 1, 18, 21)

        # Make the "songs"
        songs = []
        total_minutes = 0
        while total_minutes < piece_duration_minutes:
            song = Song(self)
            songs.append(song)
            total_minutes += song.duration_minutes

        # Make notation
        previous_duration = None
        for song in songs:
            for bar in song.bars:
                for part in bar.parts:
                    measure = Measure()
                    if bar.tempo:
                        measure.insert(0, MetronomeMark(number=bar.tempo, referent=Duration(1)))
                        measure.leftBarline = 'double'




                    if bar.duration != previous_duration:
                        ts = TimeSignature('{}/4'.format(bar.duration))
                        measure.timeSignature = ts

                    # Fix Durations
                    durations = [note['duration'] for note in part['notes']]

                    components_list = split_at_beats(durations)
                    components_list = [join_quarters(note_components) for note_components in components_list]
                    for note, components in zip(part['notes'], components_list):
                        note['durations'] = components


                    for note in part['notes']:
                        if note['pitch'] == 'rest':
                            n = Rest()
                        if isinstance(note['pitch'], list):
                            pitches = []
                            for pitch_number in note['pitch']:
                                p = Pitch(pitch_number)
                                # Force all flats
                                if p.accidental.name == 'sharp':
                                    p = p.getEnharmonic()
                                pitches.append(p)
                            n = Chord(notes=pitches)

                            # TODO add slurs
                            # TODO add glissandos
                            # TODO add -50 cent marks


                        else:
                            p = Pitch(note['pitch'])
                            # Force all flats
                            if p.accidental.name == 'sharp':
                                p = p.getEnharmonic()
                            n = Note(p)

                            # TODO add slurs
                            # TODO add glissandos
                            # TODO add -50 cent marks

                        d = Duration()
                        d.fill(note['durations'])
                        n.duration = d

                        measure.append(n)

                    self.parts.d[part['instrument_name']].append(measure)
                previous_duration = bar.duration


class Song(object):
    def __init__(self, piece):
        """
        self.duration = total song duration
        self.bars =
            bar.parts =
                part['instrument_name']
                part['notes']
                    note['pitch']
                    note['duration'] = total note duration


        """

        self.initial_root = random.randint(0, 11)
        self.harmony_generator = get_harmony_generator()
        # TODO choose roots

        self.form = form.choose()
        self.bars = self.form.bars

        self.duration_beats = self.form.duration
        self.tempo = random.randint(55, 80)
        self.bars[0].tempo = self.tempo
        self.duration_minutes = self.duration_beats / float(self.tempo)

        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]
            bar_type.harmonic_rhythm = harmonic_rhythm.choose(bar_type.duration)

            bar_type.parts[1]['notes']= [{
                'duration': harm_dur,
                'pitch': self.choose_harmony()
            } for harm_dur in bar_type.harmonic_rhythm]




        for bar in self.bars:
            bar.parts = bar.type_obj.parts

    def choose_root(self):
        return random.randint(0, 11)


        # if not self.root_sequence:
        #     self.root_sequence = [random.randint(0, 11)]
        # last = self.root_sequence[-1]

        # root_motion = weighted_choice([
        #     7,
        #     5,
        #     2,
        #     10,
        #     0,
        #     3,
        #     8,
        #     4,
        #     7,
        #     1,
        #     11,
        #     6
        # ], [
        #     .2,
        #     .2,



        # ])
        # return (last + root_motion) % 12

    def choose_harmony(self):
        root = self.choose_root()
        chord_type = self.harmony_generator.next()
        return self.build_chord(root, chord_type)

    def build_chord(self, root, chord_type):
        return [p + root + 48 for p in chord_type]





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
        if 'muse' in sys.argv:
            piece.score.show('musicxml', '/Applications/MuseScore.app')
        elif 'fin' in sys.argv:
            piece.score.show('musicxml', '/Applications/Finale 2012.app')
        else:
            piece.score.show('musicxml', '/Applications/Sibelius 7.app')

