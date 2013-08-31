from utils import weighted_choice, scale_list


def main():
    pass


def get_weighted_meter():
    beat_types = [
        [0, 2],
        [1, 3],
        [.5, 1.5, 2.5, 3.5],
        [.25, .75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]
    ]
    beat_type_weights = scale_list([6, 5, 4, 1])

    beats = []
    weights = []
    for beat_type, w in zip(beat_types, beat_type_weights):
        weight = w / len(beat_type)
        for beat in beat_type:
            weights.append(weight)
            beats.append(beat)
    return beats, weights


METER_WEIGHTS = get_weighted_meter()


def choose_meter_position():
    beats, weights = METER_WEIGHTS
    return weighted_choice(beats, weights)


if __name__ == '__main__':
    main()
