from collections import defaultdict
import random

from montreal.utils import divide

def choose_solo_rhythm():
    rest_beginning = random.choice([True, False, False, False, False])
    rest_middle = random.choice([True, True, False])
    rest_end = random.choice([True, True, True, False, False])

    rests = [rest_beginning, rest_middle, rest_end]
    num_rests = rests.count(True)

    min_num_divs = 3 + num_rests

    num_divs = random.randint(min_num_divs, 9)

    divs = divide(16, num_divs)

    notes = [{'pitch': None, 'duration': div / 4.0} for div in divs]

    if rest_beginning:
        notes[0]['pitch'] = 'rest'

    if rest_end:
        notes[-1]['pitch'] = 'rest'

    if rest_middle:
        if rest_beginning:
            start = 2
        else:
            start = 1
        if rest_end:
            end = -2
        else:
            end = -1
        middle_rest_index = random.choice(range(len(notes))[start:end])
        notes[middle_rest_index]['pitch'] = 'rest'

    return notes


def get_harmonies(parts):
    beat_map = defaultdict(list)
    for part in parts:
        beat = 0
        for note in part['notes']:
            dur = int(note['duration'] * 4)
            for b in range(dur):
                if note['pitch'] != 'rest':
                    beat_map[beat].append(note)
                beat += 1

    harmonies = []
    for beat in beat_map:
        harmony = []
        for note in beat_map[beat]:
            harmony.append(note['pitch'])
        harmonies.append(harmony)
    return harmonies


def get_unchosen_notes(parts):
    result = []
    for part in parts:
        for note in part['notes']:
            if note['pitch'] == None:
                result.append((note, part['instrument_name']))
    return result


def main():
    instruments = ['vln', 'gtr']
    parts = [{'instrument_name': i, 'notes': choose_solo_rhythm()} for i in instruments]
    
    
    unchosen_notes = get_unchosen_notes()
    while len(unchosen_notes) > 0:
        note, instrument = random.choice(unchosen_notes)
        
        valid = False
        while not valid:
            # TODO figure out how to validate melodic motion
            note['pitch'] = random.choice(range(60, 80))  # TODO choose from notes in the instrument's range
            
            harmonies = get_harmonies(parts)
            valid = validate_harmonies(harmonies)

        unchosen_notes = get_unchosen_notes()
    
    print parts
   
    
    