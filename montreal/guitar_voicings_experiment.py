OPEN_STRINGS = [40, 45, 50, 55, 59, 64]
ALL_PITCHES = range(OPEN_STRINGS[0], OPEN_STRINGS[-1] + 16)
STRING_PITCHES = [range(p, p + 16) for p in OPEN_STRINGS]


def get_playable_voicings(pitch_classes):
    allowed_pitches = []
    for string in STRING_PITCHES:
        string_allowed = []
        for p in string:
            if p % 12 in pitch_classes:
                string_allowed.append(p)
        allowed_pitches.append(string_allowed)
    return allowed_pitches


def pick_voicing(pitch_classes):
    voicings = get_playable_voicings(pitch_classes)

    # prefer ones that are easier to play
    # prefer ones with bigger intervals on the bottom and smaller on the top (is there some way)