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
from chord_types import get_chord_type, diatonic_scales_for_harmony, other_scales_for_harmony
from melody_rhythm import get_melody_rhythm
import scored_ornaments
from bass import next_bass_note
from violin import next_violin_dyad
from simple_accompaniment import next_simple_accompaniment_dyad
from vibraphone import random_vibraphone_voicing, next_vibraphone_chord
import animal_play_harmony
import scalar_ornaments


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

    if n == None:
        # Choose the number of notes in the ornament
        if prev_duration >= 0.75:
            n = weighted_choice([1, 2, 3, 4, 5, 6], [3, 3, 4, 5, 4, 3])
        else:
            n = weighted_choice([1, 2, 3], [3, 4, 5])

    interval = b - a
    abs_interval = abs(interval)
    direction = 0
    if interval > 0:
        direction = 1
    if interval < 0:
        direction = -1

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
            ('C4', 'C7'),     # Flute     60 96
            ('B-3', 'G#6'),   # Oboe      58 92
            ('D3', 'G6'),     # Clarinet  50 91
            ('D-3', 'A-5'),   # Sax       49 80
            ('E3', 'B-5'),    # Trumpet   52 82
            ('G3', 'B6'),     # Violin
            ('F3', 'F6'),     # Vibraphone
            ('E1', 'G3')      # Bass
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
        lowest_notes = [self.d[name].lowest_note.ps for name in soloists]
        lowest = int(max(lowest_notes))
        highest_notes = [self.d[name].highest_note.ps for name in soloists]
        highest = int(min(highest_notes))
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


        if self.movement <= 5:
            # Medium
            tempo_options = range(56, 66, 2)
        elif self.movement in [6, 8, 10, 12]:
            # Fast
            tempo_options = range(66, 78, 2)
        elif self.movement in [7, 9, 11]:
            # Slow
            tempo_options = range(42, 54, 2)
        elif self.movement in [13, 14]:
            # Slower
            tempo_options = range(36, 42, 2)
        elif self.movement > 14:
            # Grind to a halt
            tempo_options = range(22, 34, 2)

        self.tempo = random.choice(tempo_options)


        self.bars[0].tempo = self.tempo
        self.duration_minutes = self.duration_beats / float(self.tempo)


        root = random.randint(0, 12)
        self.harmony_history = [[(p * root) % 12 for p in get_chord_type()]]



        # for each bar_type pick a transposition pattern
        # for each bar of that type, assign the next transposition in the pattern
        # make a sub register of the soloists' common register for the bar_type,
        # that has a buffer to allow the melody to be transposed the amount that it will be transposed
        trans_patterns = {
            'descending': [
                [0, -1, -2, -3, -4],
                [0, -2, -1, -3, -2],
                [0, -1, -3, -5, -7],
                [0, -2, -4, -6, -8],
                [0, -2, -4, -5, -7],
            ],
            'ascending': [
                [0, 1, 2, 3, 4],
                [0, 2, 1, 3, 2],
                [0, 2, 4, 5, 7],
                [0, 2, 3, 5, 7],
                [0, 2, 4, 6, 8],
            ]
        }
        for name in self.form.bar_types:
            bar_type = self.form.bar_types[name]

            bar_type.direction = random.choice(trans_patterns.keys())
            options = trans_patterns[bar_type.direction]
            bar_type.trans_pattern = random.choice(options)
            bar_type.trans_pattern = bar_type.trans_pattern[:bar_type.count + 1]


            if bar_type.direction == 'descending':
                bar_type.furthest_transposition = min(bar_type.trans_pattern)
                bar_type.register = self.melody_register[abs(bar_type.furthest_transposition):]
            else:
                bar_type.furthest_transposition = max(bar_type.trans_pattern)
                bar_type.register = self.melody_register[:-bar_type.furthest_transposition]

        bar_type_counter = Counter()
        for bar in self.bars:
            bar_type = self.form.bar_types[bar.type]
            i = bar_type_counter[bar.type]
            bar.transposition = bar_type.trans_pattern[i]
            bar_type_counter[bar.type] += 1


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
            bar_type.melody = self.choose_melody_notes(bar_type.duration, bar_type.harmony, bar_type)


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


            # transposition = weighted_choice(
            #     [-2, -1, 1, 2],
            #     [10, 12, 8, 12]
            # )

            transposition = self.add_soloists_melody(soloists, bar)

            if transposition != 0:
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
                p = random.randint(violin_lowest + 7, violin_highest - 18)
                rand_interval = random.randint(-7, 7)
                violin_prev_dyad = [p, p + rand_interval]


                history['vln'].append(violin_prev_dyad)

            violin = []
            for chord in bar.harmony:
                pitch = next_violin_dyad(history['vln'][-1], chord['pitch'], violin_lowest, violin_highest)

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

                        p = random.randint(lower_limit, higher_limit)
                        rand_interval = random.randint(-4, 4)
                        prev_dyad = [p, p + rand_interval]

                        history[acc].append(prev_dyad)


                    acc_notes = []
                    for chord in bar.harmony:
                        pitch = next_simple_accompaniment_dyad(history[acc][-1], chord['pitch'], lowest, highest)

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

    def is_melody_in_instrument_register(self, melody, instrument_name):
        instrument = self.instruments.d[instrument_name]
        register = instrument.all_notes

        return self.is_melody_in_register(melody, register)

    def is_melody_in_register(self, melody, register):
        for note in melody:
            if note['pitch'] != 'rest' and note['pitch'] not in register:
                return False
            for orn in note.get('ornaments', []):
                if orn['pitch'] not in register:
                    return False
        return True

    def can_transpose(self, transposition, melody, instrument_name):
        instrument = self.instruments.d[instrument_name]
        register = instrument.all_notes

        for note in melody:
            if note['pitch'] != 'rest' and note['pitch'] + transposition not in register:
                return False
            for orn in note.get('ornaments', []):
                if orn['pitch'] + transposition not in register:
                    return False
        return True

    def transpose_melody(self, melody, transposition):
        new_melody = []
        for note in melody:
            new_note = note.copy()

            if note['pitch'] == 'rest':
                new_note['pitch'] = 'rest'
            else:
                new_note['pitch'] = note['pitch'] + transposition

            new_note['ornaments'] = []
            for orn in note.get('ornaments', []):
                new_orn = orn.copy()
                new_orn['pitch'] = orn['pitch'] + transposition
                new_note['ornaments'].append(new_orn)

            new_melody.append(new_note)
        return new_melody

    def add_soloists_melody(self, soloists, bar):
        transposition = bar.transposition

        melody = self.transpose_melody(bar.melody, transposition)

        for soloist in soloists:
            can_go_up = self.can_transpose(12, melody, soloist)
            can_go_down = self.can_transpose(-12, melody, soloist)

            if not self.is_melody_in_instrument_register(melody, soloist):
                if can_go_up:
                    melody = self.transpose_melody(melody, 12)
                if can_go_down:
                    melody = self.transpose_melody(melody, -12)

            else:
                if soloist in ['fl', 'ob'] and can_go_up and random.random() < .8:
                    melody = self.transpose_melody(melody, 12)
                elif soloist == 'cl':
                    if random.random() < .8:
                        options = [None]
                        if can_go_up:
                            options.append(12)
                        if can_go_down:
                            options.append(-12)
                        trans = random.choice(options)
                        if trans:
                            melody = self.transpose_melody(melody, trans)
                elif soloist in ['sax', 'tpt'] and can_go_down and random.random() < .4:
                    melody = self.transpose_melody(melody, -12)

            bar.parts.append({
                'instrument_name': soloist,
                'notes': melody,
            })

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

    def choose_melody_notes(self, duration, harmonies, bar_type):
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

        self.choose_melody_pitches(notes, bar_type.register, harmonies, start_with_rest)

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


    def add_scalar_ornament(self, note, prev, harmonies):
            interval = prev['pitch'] - note['pitch']
            if interval > 0:
                direction = 'ascending'
            if interval < 0:
                direction = 'descending'
            if interval == 0:
                direction = random.choice(['ascending', 'descending'])

            # Choose the number of notes in the ornament
            if prev['duration'] >= 1:
                n = weighted_choice([1, 2, 3, 4, 5, 6], [2, 3, 4, 6, 5, 4])
            elif prev['duration'] >= 0.75:
                n = weighted_choice([1, 2, 3], [1, 2, 4])
            else:
                n = random.randint(1, 2)

            orn = scalar_ornaments.choose(n, direction)

            harm = []
            for chord in harmonies:
                for p in chord:
                    if p not in harm:
                        harm.append(p)

            scale_options = diatonic_scales_for_harmony(harm)

            if random.random() < .16 or not scale_options:
                scale_options = other_scales_for_harmony(harm)

            if scale_options:
                scale_type = random.choice(scale_options)

                note_pitch = int(note['pitch'])

                note_pitch_class = note_pitch % 12

                diff = note_pitch - note_pitch_class
                scale = []
                for octave in [diff - 12, diff, diff + 12]:
                    for pc in scale_type:
                        p = pc + octave
                        scale.append(p)

                i = scale.index(note_pitch)
                scale = scale[i - 2:i + 3]

                orn_type = []
                for i in orn:
                    pitch = scale[i + 2]
                    orn_type.append(pitch)

                return orn_type

    def add_chromatic_interval(self, note, prev):
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
        return orn_type

    def add_ornament(self, note, prev, harmonies, first):
        if prev['duration'] <= .25 or random.random() < .1:
            return

        # Choose between three completely different ways of making ornaments

        orn_type = None
        rand = random.random()

        if rand < .7:
            orn_type = self.add_scalar_ornament(note, prev, harmonies)
        elif rand < .9:
            orn_type = ornament_bridge(
                prev['pitch'],
                note['pitch'],
                n=None,
                prev_duration=prev['duration'],
                width=2
            )

        if not orn_type or rand >= .9:
            orn_type = self.add_chromatic_interval(note, prev)


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
