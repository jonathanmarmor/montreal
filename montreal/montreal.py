#!/usr/bin/env python

import sys
import datetime
import random
from collections import defaultdict

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
from utils import S
from utils import get_simul
from utils import set_start_end
from utils import get_at
import harmonic_rhythm
import form
from chord_types import get_harmony_generator
from melody_rhythm import get_melody_rhythm


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
            ('G3', 'B6'),  # Violin
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

        if ranges:
            # Don't make a piece, just show the instrument ranges
            for inst, part in zip(self.instruments.l, self.parts.l):
                measure = Measure()
                measure.timeSignature = TimeSignature('4/4')
                low = Note(inst.lowest_note)
                measure.append(low)
                high = Note(inst.highest_note)
                measure.append(high)
                part.append(measure)
            return


        # 18 to 21 minutes
        piece_duration_minutes = scale(random.random(), 0, 1, 18, 21)

        # Make the "songs"
        songs = []
        total_minutes = 0
        n = 1
        while total_minutes < piece_duration_minutes:
            print 'Song {}'.format(n)
            n += 1
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
        self.piece = piece
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

            bar_type.parts[0]['notes'] = self.choose_melody_notes(bar_type.duration, bar_type.parts[1]['notes'])

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

    def choose_violin_register(self):
        all_notes = self.piece.instruments.vln.all_notes
        octave = weighted_choice([0, 1], [.6, .4]) * 12
        lowest = octave + random.randint(0, 12)
        width = random.randint(13, 17)
        highest = lowest + width
        return all_notes[lowest:highest]

    def choose_melody_notes(self, duration, harmonies):
        # return a list of {pitch, duration} dicts
        notes = []

        # choose a register
        register = self.choose_violin_register()
        register_by_pitch_classes = defaultdict(list)
        for p in register:
            register_by_pitch_classes[p % 12].append(p)

        rhythm = get_melody_rhythm(duration)

        for r in rhythm:
            notes.append({
                'pitch': None,
                'duration': r
            })

        self.choose_melody_pitches(notes, register, harmonies)

        return notes


    def choose_melody_pitches(self, notes, register, harmonies):
        print 'Choosing pitches'
        for h in harmonies:
            h['pitch'] = [p % 12for p in h['pitch']]

        set_start_end(notes)
        set_start_end(harmonies)

        previous_note_index = random.choice(range(len(register)))

        for note in notes:
            note_harmonies = []
            for b in frange(note['start'], note['duration'], .25):
                h = get_at(b, harmonies)
                h = h['pitch']
                if h not in note_harmonies:
                    note_harmonies.append(h)

            for width in range(1, 6):
                lowest = previous_note_index - width
                if lowest < 0:
                    lowest = 0
                highest = previous_note_index + width
                temp_register = register[lowest:highest + 1]
                pitch_options = [p for p in temp_register if p in note_harmonies]
                width += 1
                if len(pitch_options) > 0:
                    break

            if len(pitch_options) == 0:
                lowest = previous_note_index - 2
                if lowest < 0:
                    lowest = 0
                highest = previous_note_index + 2
                temp_register = register[lowest:highest + 1]
                pitch_options = [p for p in temp_register]

            note['pitch'] = random.choice(pitch_options)




        # simul = get_simul([notes, harmonies])








        # REMEMBER
        # 1. voice leading (chromatic, diatonic, pentatonic)
        # 2. harmonies (chord tones, diatonic)


        # offset = 0
        # for harm in harmonies:
        #     harm_dur = harm['duration']
        #     chord_pcs = [h % 12 for h in harm['pitch']]

        #     target_pc = random.choice(chord_pcs)
        #     target = random.choice(register_by_pitch_classes[target_pc])


        #     rhythm = get_melody_rhythm(harm_dur)

        #     for r in rhythm:
        #         notes.append({
        #             'pitch': target,  # TODO change
        #             'duration': r
        #         })

        #     offset += harm_dur











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

