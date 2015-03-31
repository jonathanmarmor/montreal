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
from chord_types import get_chord_type
from melody_rhythm import get_melody_rhythm
import scored_ornaments
from bass import next_bass_note
from violin import next_violin_note
from simple_accompaniment import next_simple_accompaniment_note
from vibraphone import random_vibraphone_voicing, next_vibraphone_chord
import animal_play_harmony


soloists_history = Counter()


def frange(x, y, step=1.0):
    if step > 0:
        while x < y:
            yield x
            x += step
    if step < 0:
        while x > y:
            yield x
            x += step


def choose(options, chosen):
    choice = random.choice(options)
    if chosen and chosen[-1] == choice:
        choice = choose(options, chosen)
    return choice


def ornament_bridge(a, b, n=None, prev_duration=0.75, width=2):
    """Find notes that bridge the interval between a and b"""

    interval = b - a
    abs_interval = abs(interval)
    direction = 0
    if interval > 0:
        direction = 1
    if interval < 0:
        direction = -1

    if n == None:
        # Choose the number of notes in the ornament
        max_notes = 3
        if prev_duration >= 0.75:
            max_notes = 6
        n = random.randint(1, max_notes)

    if direction == 0:
        option_groups = [range(int(a - width), int(a + width + 1))] * n

    else:
        offset_interval = float(interval) / n
        option_groups = []
        for offset in list(frange(a, b, offset_interval)):
            middle = int(round(offset))
            opts = range(middle - width, middle + width + 1)
            option_groups.append(opts)

    # Prevent the last note in the ornament from being the target note.
    if b in option_groups[-1]:
        option_groups[-1].remove(b)

    ornaments = []
    for opts in option_groups:
        choice = choose(opts, ornaments)
        ornaments.append(choice)

    return ornaments


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

    def soloists_shared_register(self):
        soloists = [
            'ob',
            'cl',
            'sax',
            'fl',
            'tpt',
        ]
        lowest = int(max([self.d[name].lowest_note.ps for name in soloists]))
        highest = int(min([self.d[name].highest_note.ps for name in soloists]))
        return range(lowest, highest + 1)


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

        self.duet_options = [
            ('ob', 'sax'),
            ('fl', 'sax'),
            ('cl', 'sax'),
            ('ob', 'tpt'),
            ('sax', 'tpt'),
            ('cl', 'tpt'),
            ('fl', 'tpt'),
            ('fl', 'ob'),
            ('fl', 'cl'),
            ('ob', 'cl'),
        ]

        # 8 to 12 minutes
        max_duration = 12
        piece_duration_minutes = scale(random.random(), 0, 1, 8, max_duration)

        # Make the "songs"
        songs = []
        total_minutes = 0
        n = 1
        while total_minutes < piece_duration_minutes - .75:
            print
            print 'Song', n
            song = Song(self, n)
            songs.append(song)
            n += 1
            print 'Song Duration:', int(round(song.duration_minutes * 60.0))
            print 'Tempo:', song.tempo
            print 'Number of Beats:', song.duration_beats
            total_minutes += song.duration_minutes

        _minutes, _seconds = divmod(total_minutes, 1.0)
        print
        print 'Total Duration: {}:{}'.format(int(_minutes), int(round(_seconds * 60)))
        print

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
                        else:
                            if isinstance(note['pitch'], list):
                                pitches = []
                                for pitch_number in note['pitch']:
                                    p = Pitch(pitch_number)
                                    # Force all flats
                                    if p.accidental.name == 'sharp':
                                        p = p.getEnharmonic()
                                    pitches.append(p)
                                n = Chord(notes=pitches)

                            else:
                                p = Pitch(note['pitch'])
                                # Force all flats
                                if p.accidental.name == 'sharp':
                                    p = p.getEnharmonic()
                                n = Note(p)

                        d = Duration()
                        if note['duration'] == 0:
                            d.quarterLength = .125
                            d = d.getGraceDuration()
                        else:
                            d.fill(note['durations'])
                        n.duration = d

                        measure.append(n)

                    self.parts.d[part['instrument_name']].append(measure)
                previous_duration = bar.duration


class Song(object):
    def __init__(self, piece, movement):
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
        self.movement = movement
        self.prev_root = random.randint(0, 11)

        self.instruments = self.piece.instruments

        self.melody_register = self.instruments.soloists_shared_register()


        history = {}
        for name in self.instruments.names:
            history[name] = []



        self.form = form.choose()

        print self.form.form_string

        self.bars = self.form.bars

        self.duration_beats = self.form.duration


        if self.movement <= 6:
            tempo_options = range(50, 62, 2)
        elif self.movement > 6 and self.movement <= 11:
            speed = random.choice(['fast', 'fast', 'slow'])
            if speed == 'fast':
                tempo_options = range(60, 72, 2)
            else:
                tempo_options = range(42, 54, 2)
        elif self.movement > 11 and self.movement <= 14:
            tempo_options = range(36, 48, 2)
        if self.movement > 14:
            tempo_options = range(26, 38, 2)

        self.tempo = random.choice(tempo_options)


        self.bars[0].tempo = self.tempo
        self.duration_minutes = self.duration_beats / float(self.tempo)


        root = random.randint(0, 12)
        self.harmony_history = [[(p * root) % 12 for p in get_chord_type()]]

        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]
            bar_type.harmonic_rhythm = harmonic_rhythm.choose(bar_type.duration)

            # Harmony
            bar_type.harmony = []
            for harm_dur in bar_type.harmonic_rhythm:

                chord_type = get_chord_type()

                # print 'CHORD TYPE:', chord_type

                harmony = animal_play_harmony.choose_next_harmony(self.harmony_history, chord_type)
                self.harmony_history.append(harmony)

                # print 'HARMONY:', harmony

                h = {
                    'duration': harm_dur,
                    'pitch': harmony
                }
                bar_type.harmony.append(h)

            # Melody
            bar_type.melody = self.choose_melody_notes(bar_type.duration, bar_type.harmony)


        #### Turn Bar Types into Bars

        size = 1
        for bar in self.bars:
            bar.parts = []

            bar.melody = bar.type_obj.melody
            bar.harmony = bar.type_obj.harmony

            if not self.piece.duet_options:
                self.piece.duet_options = [
                    ('ob', 'sax'),
                    ('fl', 'sax'),
                    ('cl', 'sax'),
                    ('ob', 'tpt'),
                    ('sax', 'tpt'),
                    ('cl', 'tpt'),
                    ('fl', 'tpt'),
                    ('fl', 'ob'),
                    ('fl', 'cl'),
                    ('ob', 'cl'),
                ]

            soloist_options = [
                'ob',
                'cl',
                'sax',
                'fl',
                'tpt',
            ]
            soloist_weights = [
                35,
                26,
                16,
                13,
                10,
            ]
            soloists = []

            if size == 1:
                soloist = weighted_choice(soloist_options, soloist_weights)
                soloists.append(soloist)
                soloist_options.remove(soloist)
            elif size == 2:
                duet = random.choice(self.piece.duet_options)
                self.piece.duet_options.remove(duet)
                for soloist in duet:
                    soloists.append(soloist)
                    soloist_options.remove(soloist)

            soloists_history[tuple(sorted(soloists))] += 1


            transposition = self.add_soloists_melody(soloists, bar)

            if transposition != 0:
                melody = []
                print 'before', bar.melody
                for note in bar.melody:
                    if note['pitch'] == 'rest':
                        new_pitch = 'rest'
                    else:
                        new_pitch = note['pitch'] + transposition
                    melody.append({
                        'pitch': new_pitch,
                        'duration': note['duration']
                    })
                bar.melody = melody
                print 'after', bar.melody

                harmony = []
                for note in bar.harmony:
                    harmony.append({
                        'pitch': [p + transposition for p in note['pitch']],
                        'duration': note['duration']
                    })
                bar.harmony = harmony


            # Violin
            violin_lowest = self.piece.instruments.vln.lowest_note.ps
            violin_highest = self.piece.instruments.vln.highest_note.ps
            if not history['vln']:
                violin_prev_pitch = random.randint(violin_lowest + 7, violin_highest - 18)
                history['vln'].append(violin_prev_pitch)

            violin = []
            for chord in bar.harmony:
                pitch = next_violin_note(history['vln'][-1], chord['pitch'], violin_lowest, violin_highest)

                violin.append({
                    'duration': chord['duration'],
                    'pitch': pitch,
                })
                history['vln'].append(pitch)

            # Vibraphone
            vib_lowest = int(self.piece.instruments.vib.lowest_note.ps)
            vib_highest = int(self.piece.instruments.vib.highest_note.ps)
            if not history['vib']:
                prev_vib_chord = random_vibraphone_voicing(vib_lowest, vib_highest)
                history['vib'].append(prev_vib_chord)

            vibraphone = []
            for harm in bar.harmony:

                vib_pitches = next_vibraphone_chord(history['vib'][-1], harm['pitch'], vib_lowest, vib_highest)

                vibraphone.append({
                    'duration': harm['duration'],
                    'pitch': vib_pitches,
                })


            # Bass
            bass_lowest = self.piece.instruments.bs.lowest_note.ps
            bass_highest = self.piece.instruments.bs.highest_note.ps
            if not history['bs']:
                bass_prev_pitch = random.randint(bass_lowest, bass_lowest + 18)
                history['bs'].append(bass_prev_pitch)


            bass = []
            for chord in bar.harmony:
                pitch = next_bass_note(history['bs'][-1], chord['pitch'], bass_lowest, bass_highest)

                bass.append({
                    'duration': chord['duration'],
                    'pitch': pitch,
                })
                history['bs'].append(pitch)


            bar.parts.extend([
                {
                    'instrument_name': 'vln',
                    'notes': violin,
                },
                {
                    'instrument_name': 'vib',
                    'notes': vibraphone,
                },
                {
                    'instrument_name': 'bs',
                    'notes': bass,
                },
            ])

            if size > 1:
                num_accompanists = 2  # random.randint(2, len(soloist_options))
                accompanists = random.sample(soloist_options, num_accompanists)
                for acc in accompanists:
                    soloist_options.remove(acc)

                    lowest = self.piece.instruments.d[acc].lowest_note.ps
                    highest = self.piece.instruments.d[acc].highest_note.ps
                    if not history[acc]:
                        quarter_of_register = (highest - lowest) / 4
                        lower_limit = int(lowest + quarter_of_register)
                        higher_limit = int(highest - quarter_of_register)

                        prev_pitch = random.randint(lower_limit, higher_limit)
                        history[acc].append(prev_pitch)

                    acc_notes = []
                    for chord in bar.harmony:
                        pitch = next_simple_accompaniment_note(history[acc][-1], chord['pitch'], lowest, highest)

                        acc_notes.append({
                            'duration': chord['duration'],
                            'pitch': pitch,
                        })
                        history[acc].append(pitch)

                    bar.parts.append({
                        'instrument_name': acc,
                        'notes': acc_notes,
                    })

            # Put rests in instruments that aren't playing in this bar
            bar_of_rests = [{
                'pitch': 'rest',
                'duration': bar.duration,
            }]
            for inst in soloist_options:
                bar.parts.append({
                    'instrument_name': inst,
                    'notes': bar_of_rests,
                })

            size = 1 if size > 1 else 2

    def add_soloists_melody(self, soloists, bar):
        melody_pitches = []
        for note in bar.melody:
            if note['pitch'] != 'rest':
                for orn in note.get('ornaments', []):
                    melody_pitches.append(orn['pitch'])
                melody_pitches.append(note['pitch'])

        melody_lowest = min(melody_pitches)
        melody_highest = max(melody_pitches)

        if len(soloists) == 2:
            lowest_a = int(self.piece.instruments.d[soloists[0]].lowest_note.ps)
            highest_a = int(self.piece.instruments.d[soloists[0]].highest_note.ps)
            register_a = range(lowest_a, highest_a + 1)

            lowest_b = int(self.piece.instruments.d[soloists[1]].lowest_note.ps)
            highest_b = int(self.piece.instruments.d[soloists[1]].highest_note.ps)
            register_b = range(lowest_b, highest_b + 1)

            register = list(set(register_a).intersection(set(register_b)))

        else:
            lowest = int(self.piece.instruments.d[soloists[0]].lowest_note.ps)
            highest = int(self.piece.instruments.d[soloists[0]].highest_note.ps)

            register = range(lowest, highest + 1)

        register_lowest = min(register)
        register_highest = max(register)

        if melody_lowest >= register_lowest and melody_highest <= register_highest:
            # No transposition necessary

            for soloist in soloists:
                bar.parts.append({
                    'instrument_name': soloist,
                    'notes': bar.melody,
                })
        else:
            print 'melody_lowest', melody_lowest, 'register_lowest', register_lowest, 'melody_highest', melody_highest, 'register_highest', register_highest

            for soloist in soloists:
                bar.parts.append({
                    'instrument_name': soloist,
                    'notes': bar.melody,
                })




        transposition = 0
        # transposition = weighted_choice(
        #     [-2, -1, 1, 2],
        #     [10, 12, 8, 12]
        # )
        return transposition


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
        chord_type = get_chord_type()
        return self.build_chord(root, chord_type)

    def build_chord(self, root, chord_type):
        return [(p + root) % 12 for p in chord_type]

    # def choose_violin_register(self):
    #     lowest = random.randint(0, 18)
    #     width = random.randint(13, 22)
    #     highest = lowest + width
    #     return self.vln_all_notes[lowest:highest]

    def choose_melody_notes(self, duration, harmonies):
        # return a list of {pitch, duration} dicts
        notes = []

        # choose a register
        # register = self.choose_violin_register()
        # register_by_pitch_classes = defaultdict(list)
        # for p in register:
        #     register_by_pitch_classes[p % 12].append(p)

        rhythm = get_melody_rhythm(duration)

        # One in four bars that have more than 3 notes will start with a rest
        start_with_rest = False
        if rhythm[0] <= 1.0:
            if len(rhythm) > 2 and random.random() < .4:
                start_with_rest = True

        for r in rhythm:
            notes.append({
                'pitch': None,
                'duration': r
            })

        self.choose_melody_pitches(notes, self.melody_register, harmonies, start_with_rest)

        notes = self.add_ornaments(notes)

        return notes


    def get_pitch_options(self, note_harmonies, prev):
        pitch_options = [prev - 2, prev - 1, prev + 1, prev + 2]
        pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.melody_register]
        if len(pitch_options) == 0:
            if prev % 12 in note_harmonies and random.random() < .12:
                pitch_options = [prev]
            else:
                pitch_options = [prev - 5, prev - 4, prev - 3, prev + 3, prev + 4, prev + 5]
                pitch_options = [p for p in pitch_options if p % 12 in note_harmonies and p in self.melody_register]
            # if len(pitch_options) == 0:
            #     pitch_options = [prev - 8, prev - 7, prev - 6, prev + 6, prev + 7, prev + 8]
            #     pitch_options = [p for p in pitch_options if p % 12 in note_harmonies]
        return pitch_options

    def choose_melody_pitches(self, notes, register, harmonies, start_with_rest):
        # print 'Choosing pitches'
        for h in harmonies:
            h['pitch_classes'] = [p % 12 for p in h['pitch']]

        set_start_end(notes)
        set_start_end(harmonies)

        # Pick a random pitch from the instrument's register on which to start
        previous_note_index = random.choice(range(int(len(register))))
        prev = register[previous_note_index]

        previous_note = {'duration': 1.0, 'pitch': prev}

        pitch_history = []

        first = True
        # print '-'*10
        for note in notes:
            if first and start_with_rest:
                note['pitch'] = 'rest'
                first = False
                continue
            beats = list(frange(note['start'], note['start'] + note['duration'], .25))
            note_harmonies = []
            for b in beats:
                h = get_at(b, harmonies)
                h = h['pitch_classes']
                if h not in note_harmonies:
                    note_harmonies.append(h)

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

            self.add_ornament(note, previous_note, note_harmonies, first)

            # print note

            prev = note['pitch']
            previous_note = note
            pitch_history.append(note['pitch'])

            first = False


    def add_ornament(self, note, prev, harmonies, first):
        if prev['duration'] <= .25 or random.random() < .1:
            return

        # Choose between two completely different ways of making ornaments

        if first or random.random() < .4:
            # harmonies = [p for p in [h for h in harmonies]]

            interval = prev['pitch'] - note['pitch']
            if interval > 0:
                direction = 'ascending'
            if interval < 0:
                direction = 'descending'
            if interval == 0:
                direction = random.choice(['ascending', 'descending'])

            # Choose the number of notes in the ornament
            if prev['duration'] >= 1:
                max_notes = 4
                n = weighted_choice(range(1, max_notes + 1), [10, 9, 7, 5])
            elif prev['duration'] >= 0.75:
                max_notes = 3
                n = random.randint(1, max_notes)
            else:
                max_notes = 2
                n = random.randint(1, max_notes)

            orn = scored_ornaments.choose(n, direction)

            np = int(note['pitch'])
            orn_type = [np + p for p in orn]

        else:

            orn_type = ornament_bridge(
                prev['pitch'],
                note['pitch'],
                n=None,
                prev_duration=prev['duration'],
                width=2
            )

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
