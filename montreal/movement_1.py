# import random
# from collections import defaultdict

# from music21.note import Note, Rest
# from music21.pitch import Pitch
# from music21.stream import Stream, Measure
# from music21.meter import TimeSignature
# from music21.duration import Duration
# from music21.spanner import Glissando, Slur

# from utils import weighted_choice, count_intervals, frange, fill, divide, split_at_beats, join_quarters
# import song_forms


# # def get_harmonies(parts):
# #     beat_map = defaultdict(list)
# #     for part in parts:
# #         beat = 0
# #         for note in part['notes']:
# #             dur = int(note['duration'] * 4)
# #             for b in range(dur):
# #                 if note['pitch'] != 'rest':
# #                     beat_map[beat].append(note)
# #                 beat += 1

# #     harmonies = []
# #     for beat in beat_map:
# #         harmony = []
# #         for note in beat_map[beat]:
# #             harmony.append(note['pitch'])
# #         harmonies.append(harmony)
# #     return harmonies


# # def validate_harmonies(harmonies):
# #     return all([validate_harmony(h) for h in harmonies])


# # def validate_harmony(harmony):
# #     harmony = [p for p in harmony if p != None]
# #     harmony = list(set([int(p % 12) for p in harmony]))
# #     harmony.sort()
# #     lowest = min(harmony)
# #     harmony = [p - lowest for p in harmony]

# #     interval_count = count_intervals(harmony)
# #     intervals = interval_count.keys()
# #     if set([1, 6, 11]).intersection(intervals):
# #         return False

# #     if harmony == [0, 4, 8]:
# #         return False

# #     return True


# # class Song(object):
# #     def __init__(self, number, piece, movement):
# #         self.number = number
# #         self.piece = piece
# #         self.movement = movement

# #         instrument_opts = piece.instruments.names[:]

# #         self.note_opts = {}
# #         for name in instrument_opts:
# #             self.note_opts[name] = piece.i.d[name].all_notes

# #         form = self.form = song_forms.choose()

# #         self.duration = len(form) * 4

# #         self.type = 'solo'
# #         if number % 2:
# #             self.type = 'ensemble'

# #         if self.type == 'solo':
# #             if len(movement.solo_ensemble_options) == 0:
# #                 movement.solo_ensemble_options = piece.i.get_unison_ensembles(min_notes=6)
# #                 print 'Hey, we ran out of unison ensembles! Cool!'
# #             solo_ensemble_hash = random.choice(movement.solo_ensemble_options.keys())
# #             self.soloists = movement.solo_ensemble_options[solo_ensemble_hash]['instruments']
# #             self.soloist_names = [s.nickname for s in self.soloists]
# #             self.soloists_shared_notes = movement.solo_ensemble_options[solo_ensemble_hash]['notes']
# #             # Remove chosen ensemble from options
# #             del movement.solo_ensemble_options[solo_ensemble_hash]

# #             # remove chosen soloists from instrument options for the song
# #             for soloist in self.soloist_names:
# #                 instrument_opts.remove(soloist)

# #             self.accompanist_names = instrument_opts

# #             len_accompanists = len(self.accompanist_names)
# #             if len_accompanists == 2:
# #                 ensemble_size = 2
# #             elif len_accompanists == 3:
# #                 ensemble_size = random.choice([2, 3])
# #             elif len_accompanists == 4:
# #                 ensemble_size = random.choice([1, 2, 3, 4])

# #             self.accompanist_names = random.sample(self.accompanist_names, ensemble_size)


# #         else:
# #             # who plays, who sits out?
# #             # ensemble_size = weighted_choice([3, 4, 5, 6], [1, 4, 5, 4])
# #             # self.ensemble_names = random.sample(instrument_opts, ensemble_size)

# #             # Everyone plays
# #             self.ensemble_names = instrument_opts


# #         # make a phrase for each unique part of the form (eg, an `a` in `abacabac`)
# #         unique_phrases = []
# #         for f in set(form):
# #             if self.type == 'solo':
# #                 PhraseClass = SoloPhrase
# #             elif self.type == 'ensemble':
# #                 PhraseClass = EnsemblePhrase
# #             unique_phrases.append(PhraseClass(piece, movement, self))

# #         # Copy the phrases in the order specified by form
# #         phrases = []
# #         for f in form:
# #             phrases.append(unique_phrases[f])

# #         # Render phrases as music21 objects
# #         for phrase in phrases:
# #             for part in phrase.parts:
# #                 measure = Measure()
# #                 if movement.first_measure:
# #                     ts = TimeSignature('4/4')

# #                     # ts.beatSequence = ts.beatSequence.subdivide(4)
# #                     ts.beamSequence = ts.beamSequence.subdivide(4)


# #                     # ts.beatSequence.partitionByList(subdivide(self.duration, 4))
# #                     # for i, b in enumerate(ts.beatSequence):
# #                     #     if b.duration.quarterLength == 4:
# #                     #         ts.beatSequence[i] = b.subdivide(2)
# #                     #         # ts.beatSequence[i][0] = b.subdivide(2)
# #                     #         # ts.beatSequence[i][1] = b.subdivide(2)
# #                     #     elif b.duration.quarterLength == 3:
# #                     #         ts.beatSequence[i] = b.subdivideByList([2, 1])
# #                     #         # ts.beatSequence[i][0] = ts.beatSequence[i].subdivide(2)
# #                     #     elif b.duration.quarterLength == 2:
# #                     #         ts.beatSequence[i] = b.subdivide(2)




# #                     measure.timeSignature = ts

# #                 self.fix_durations(part['notes'])

# #                 for note in part['notes']:
# #                     if note['pitch'] == 'rest':
# #                         n = Rest()
# #                     else:
# #                         p = Pitch(note['pitch'])
# #                         # Force all flats
# #                         if p.accidental.name == 'sharp':
# #                             p = p.getEnharmonic()
# #                         n = Note(p)

# #                         # TODO add slurs
# #                         # TODO add glissandos
# #                         # TODO add -50 cent marks

# #                     d = Duration()
# #                     d.fill(note['durations'])
# #                     n.duration = d

# #                     measure.append(n)

# #                 # if len(measure.notesAndRests) > 1:
# #                 #     measure.sliceByBeat(inPlace=True)

# #                 piece.parts.d[part['instrument_name']].append(measure)
# #             movement.first_measure = False

# #     def fix_durations(self, notes):
# #         print
# #         durations = [note['duration'] for note in notes]
# #         print 'durations:'
# #         print durations

# #         components_list = split_at_beats(durations)
# #         print 'split at beats:'
# #         print components_list

# #         components_list = [join_quarters(note_components) for note_components in components_list]
# #         print 'quarters joined:'
# #         print components_list

# #         for note, components in zip(notes, components_list):
# #             note['durations'] = components





# class Phrase(object):
#     def __init__(self, piece, movement):
#         self.piece = piece
#         self.movement = movement

#         instruments = ['vln', 'gtr']
#         parts = [{'instrument_name': i, 'notes': self.choose_solo_rhythm()} for i in instruments]

#         unchosen_notes = self.get_unchosen_notes()
#         while len(unchosen_notes) > 0:
#             note, instrument = random.choice(unchosen_notes)

#             valid = False
#             while not valid:
#                 # TODO figure out how to validate melodic motion
#                 note['pitch'] = random.choice(range(60, 80))  # TODO choose from notes in the instrument's range

#                 harmonies = get_harmonies(parts)
#                 valid = validate_harmonies(harmonies)

#             unchosen_notes = self.get_unchosen_notes()

#         print parts

#     def get_unchosen_notes(self, parts):
#         result = []
#         for part in parts:
#             for note in part['notes']:
#                 if note['pitch'] == None:
#                     result.append((note, part['instrument_name']))
#         return result

#     def choose_solo_rhythms(self):
#         rest_beginning = random.choice([True, False, False, False, False])
#         rest_middle = random.choice([True, True, False])
#         rest_end = random.choice([True, True, True, False, False])

#         rests = [rest_beginning, rest_middle, rest_end]
#         num_rests = rests.count(True)

#         min_num_divs = 3 + num_rests

#         num_divs = random.randint(min_num_divs, 9)

#         divs = divide(16, num_divs)

#         notes = [{'pitch': None, 'duration': div / 4.0} for div in divs]

#         if rest_beginning:
#             notes[0]['pitch'] = 'rest'

#         if rest_end:
#             notes[-1]['pitch'] = 'rest'

#         if rest_middle:
#             if rest_beginning:
#                 start = 2
#             else:
#                 start = 1
#             if rest_end:
#                 end = -2
#             else:
#                 end = -1
#             middle_rest_index = random.choice(range(len(notes))[start:end])
#             notes[middle_rest_index]['pitch'] = 'rest'

#         return notes


# class Song(object):
#     def __init__(object, piece, movement):
#         pass




# class Movement1(object):
#     def __init__(self, duration, piece):
#         self.duration = duration
#         self.piece = piece
#         self.songs = []
#         self.first_measure = True  # just a flag so I know to make a time signature

#         total = 0
#         while total < duration:
#             song = Song(piece, self)
#             self.songs.append(song)
#             total += song.duration

