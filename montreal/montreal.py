#!/usr/bin/env python

import sys
import datetime
import random
from collections import defaultdict, Counter

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Measure, Part, Score
from music21.meter import TimeSignature
from music21.metadata import Metadata
from music21.instrument import (
    Oboe,
    Clarinet,
    Flute,
    AltoSaxophone,
    Trumpet,
    Violin,
    Vibraphone,
    Contrabass
)
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
from utils import get_by_attr
import harmonic_rhythm
import form
from chord_types import get_harmony_generator
from melody_rhythm import get_melody_rhythm


class Instruments(object):
    def __init__(self):
        self.names = [
            'fl',
            'ob',
            'cl',
            'sax',
            'tpt',
            'vln',
            'vib',
            'bs'
        ]
        self.fl = fl = Flute()
        self.ob = ob = Oboe()
        self.cl = cl = Clarinet()
        self.sax = sax = AltoSaxophone()
        self.tpt = tpt = Trumpet()
        self.vln = vln = Violin()
        self.vib = vib = Vibraphone()
        self.bs = bs = Contrabass()

        self.l = [
            fl,
            ob,
            cl,
            sax,
            tpt,
            vln,
            vib,
            bs
        ]
        self.d = {}
        for name, inst in zip(self.names, self.l):
            inst.nickname = name
            self.d[name] = inst

        # lowest, highest notes
        ranges = [
            ('C4', 'C7'),  # Flute
            ('B-3', 'G#6'),  # Oboe
            ('D3', 'G6'),  # Clarinet
            ('D-3', 'A-5'),  # Sax
            ('E3', 'B-5'),  # Trumpet
            ('G3', 'B6'),  # Violin
            ('F3', 'F6'),  # Vibraphone
            ('E1', 'G3')  # Bass
        ]
        for r, i in zip(ranges, self.l):
            i.lowest_note = Pitch(r[0])
            i.highest_note = Pitch(r[1])
            i.all_notes = list(frange(i.lowest_note.ps, i.highest_note.ps + 1))
            i.all_notes_24 = list(frange(i.lowest_note.ps, i.highest_note.ps + 1, 0.5))


class Parts(object):
    def __init__(self, instruments):
        self.names = [
            'fl',
            'ob',
            'cl',
            'sax',
            'tpt',
            'vln',
            'vib',
            'bs'
        ]

        self.fl = fl = Part()
        self.ob = ob = Part()
        self.cl = cl = Part()
        self.sax = sax = Part()
        self.tpt = tpt = Part()
        self.vln = vln = Part()
        self.vib = vib = Part()
        self.bs = bs = Part()

        self.l = [
            fl,
            ob,
            cl,
            sax,
            tpt,
            vln,
            vib,
            bs
        ]
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
        metadata.title = 'Utah'
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


        # 8 to 12 minutes
        piece_duration_minutes = scale(random.random(), 0, 1, 8, 12)

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
                        if note['duration'] == 0:
                            d.quarterLength = .5
                            d = d.getGraceDuration()
                        else:
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
        self.prev_root = random.randint(0, 11)
        self.harmony_generator = get_harmony_generator()
        # TODO choose roots

        self.vln_all_notes = self.piece.instruments.vln.all_notes
        self.vln_register = self.choose_violin_register()

        self.form = form.choose()
        self.bars = self.form.bars

        self.duration_beats = self.form.duration
        self.tempo = random.randint(40, 50)
        self.bars[0].tempo = self.tempo
        self.duration_minutes = self.duration_beats / float(self.tempo)

        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]
            bar_type.harmonic_rhythm = harmonic_rhythm.choose(bar_type.duration)

            # Vibraphone
            vibraphone = get_by_attr(bar_type.parts, 'instrument_name', 'vib')
            vibraphone['notes'] = [{
                'duration': harm_dur,
                'pitch': self.choose_harmony()
            } for harm_dur in bar_type.harmonic_rhythm]

            # Violin
            violin = get_by_attr(bar_type.parts, 'instrument_name', 'vln')
            violin['notes'] = self.choose_melody_notes(bar_type.duration, vibraphone['notes'])

        for bar in self.bars:
            bar.parts = bar.type_obj.parts

    def choose_root(self):
        return random.randint(0, 11)

        root_motion = weighted_choice([
            7,
            5,
            2,
            10,
            3,
            8,
            4,
            9,
            1,
            11,
            0,
            6
        ], range(24, 12, -1))
        root = (self.prev_root + root_motion) % 12
        self.prev_root = root
        return root

    def choose_harmony(self):
        root = self.choose_root()
        chord_type = self.harmony_generator.next()
        return self.build_chord(root, chord_type)

    def build_chord(self, root, chord_type):
        return [p + root + 48 for p in chord_type]

    def choose_violin_register(self):
        lowest = random.randint(0, 18)
        width = random.randint(13, 22)
        highest = lowest + width
        return self.vln_all_notes[lowest:highest]

    def choose_melody_notes(self, duration, harmonies):
        # return a list of {pitch, duration} dicts
        notes = []

        # choose a register
        # register = self.choose_violin_register()
        # register_by_pitch_classes = defaultdict(list)
        # for p in register:
        #     register_by_pitch_classes[p % 12].append(p)

        rhythm = get_melody_rhythm(duration)

        for r in rhythm:
            notes.append({
                'pitch': None,
                'duration': r
            })

        self.choose_melody_pitches(notes, self.vln_register, harmonies)

        notes = self.add_ornaments(notes)

        return notes


    def get_pitch_options(self, note_harmonies, prev):
        pitch_options = [prev - 2, prev - 1, prev + 1, prev + 2]
        pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.vln_all_notes]
        if len(pitch_options) == 0:
            if prev % 12 in note_harmonies and random.random() < .12:
                pitch_options = [prev]
            else:
                pitch_options = [prev - 5, prev - 4, prev - 3, prev + 3, prev + 4, prev + 5]
                pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.vln_all_notes]
            # if len(pitch_options) == 0:
            #     pitch_options = [prev - 8, prev - 7, prev - 6, prev + 6, prev + 7, prev + 8]
            #     pitch_options = [p for p in pitch_options if p % 12 in note_harmonies]
        return pitch_options

    def choose_melody_pitches(self, notes, register, harmonies):
        # print 'Choosing pitches'
        for h in harmonies:
            h['pitch_classes'] = [p % 12 for p in h['pitch']]

        set_start_end(notes)
        set_start_end(harmonies)

        # Pick a random pitch from the instrument's register on which to start
        previous_note_index = random.choice(range(int(len(register) * .4)))
        prev = register[previous_note_index]

        for note in notes:
            beats = list(frange(note['start'], note['start'] + note['duration'], .25))
            note_harmonies = []
            for b in beats:
                h = get_at(b, harmonies)
                h = h['pitch_classes']
                if h not in note_harmonies:
                    note_harmonies.append(h)

            # print 'note_harmonies', note_harmonies

            if len(note_harmonies) == 1:
                pitch_options = self.get_pitch_options(note_harmonies[0], prev)
            else:
                pitch_options = []

                c = Counter()
                for h in note_harmonies:
                    for p in h:
                        c[p] += 1

                common = []
                for p, count in c.most_common():
                    if count == len(note_harmonies):
                        common.append(p)

                if len(common) > 0:
                    pitch_options = self.get_pitch_options(common, prev)

                if len(pitch_options) == 0:
                    ranked = [p for p, _ in c.most_common() if p not in common]

                    for p in ranked:
                        pitch_options = self.get_pitch_options([p], prev)
                        if len(pitch_options) > 0:
                            break

            if len(pitch_options) == 0:
                pitch_options = [prev - 2, prev - 1, prev + 1, prev + 2]

            note['pitch'] = random.choice(pitch_options)

            # print note['pitch'] % 12
            # print

            prev = note['pitch']

            self.add_ornament(note, prev, note_harmonies)

    def add_ornament(self, note, prev, harmonies):
        if note['duration'] < .75 or random.random() < .3:
            return

        harmonies = [p for p in [h for h in harmonies]]

        interval = note['pitch'] - prev
        if interval > 0:
            direction = 'ascending'
        if interval < 0:
            direction = 'descending'
        if interval == 0:
            direction = random.choice(['ascending', 'descending'])

        np = int(note['pitch'])

        # below = [p for p in range(np - 4,  np) if p % 12 in harmonies]
        # above = [p for p in range(np + 1,  np + 5) if p % 12 in harmonies]

        orn_types = {}
        orn_types['ascending'] = [
            [np - 1],
            [np - 2],
            [np - 1],
            [np - 2],
            [np - 1],
            [np - 2],
            [np - 1],
            [np - 2],
            [np - 2, np - 1],
            [np - 3, np - 1],
            [np - 3, np - 2],
            [np - 4, np - 2],
            [np, np - 1],
            [np, np - 2],
            [np - 1, np - 2],
            [np - 1, np - 3],
            [np - 2, np - 3],
            [np - 2, np - 4],

            [np - 1, np + 1],
            [np - 1, np + 2],
            [np - 2, np + 1],
            [np - 2, np + 2],
            [np + 1, np - 1],
            [np + 1, np - 2],
            [np + 2, np - 1],
            [np + 2, np - 2]
        ]
        orn_types['descending'] = [
            [np + 1],
            [np + 2],
            [np + 1],
            [np + 2],
            [np + 1],
            [np + 2],
            [np + 1],
            [np + 2],
            [np + 2, np + 1],
            [np + 3, np + 1],
            [np + 3, np + 2],
            [np + 4, np + 2],
            [np, np + 1],
            [np, np + 2],
            [np + 1, np + 2],
            [np + 1, np + 3],
            [np + 2, np + 3],
            [np + 2, np + 4],

            [np - 1, np + 1],
            [np - 1, np + 2],
            [np - 2, np + 1],
            [np - 2, np + 2],
            [np + 1, np - 1],
            [np + 1, np - 2],
            [np + 2, np - 1],
            [np + 2, np - 2]
        ]

        orn_type = random.choice(orn_types[direction])


        note['ornaments'] = []
        for n in orn_type:
            note['ornaments'].append({
                'pitch': n,
                'duration': 0
            })

    def add_ornaments(self, notes):
        new_notes = []
        for note in notes:
            if note.get('ornaments'):
                for orn in note['ornaments']:
                    new_notes.append(orn)
            new_notes.append(note)
        return new_notes


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
            piece.score.show('musicxml', '/Applications/Sibelius 7.5.app')
