from utils import weighted_choice, scale_list


class S(object):
    def __init__(self, *args):
        self.weighted_options = args

    def choose(self):
        weights, options = zip(*self.weighted_options)
        choice = weighted_choice(options, weights)
        if isinstance(choice, S):
            return choice.choose()
        return choice


tree = S(
    (.6, 'this is a value'),
    (.4, S(
        (.7, 25),
        (.3, ['values', 3, {'k': 'v'}])
    ))
)



def choose():
    return tree.choose()

tree = {}
tree[2] = S(
    (.3, 0),
    (.7, S(
        (.5 , 1),
        (.4, S(
            (.5, 0.5),
            (.5, 1.5)
        )),
        (.1, S(
            (.3, 0.25),
            (.4, 0.75),
            (.3, 1.25)
        ))
    ))
)
tree[4] = S(
    (.2, 0),
    (.3, 2),
    (.2, S(
        (.5, 1),
        (.5, 3)
    )),
    (.2, S(
        (.15, 0.5),
        (.4, 1.5),
        (.4, 2.5),
        (.05, 3.5),
    )),
    (.1, S(
        (0.11, 0.25),
        (0.15, 0.75),
        (0.18, 1.25),
        (0.2, 1.75),
        (0.2, 2.25),
        (0.15, 2.75),
        (0.0025, 3.25),
        (0.0075, 3.75)
    ))
)
tree[8] = S(
    (1, 0),
    (1, 0.25),
    (1, 0.5),
    (1, 0.75),
    (1, 1.0),
    (1, 1.25),
    (1, 1.5),
    (1, 1.75),
    (1, 2.0),
    (1, 2.25),
    (1, 2.5),
    (1, 2.75),
    (1, 3.0),
    (1, 3.25),
    (1, 3.5),
    (1, 3.75),
    (1, 4.0),
    (1, 4.25),
    (1, 4.5),
    (1, 4.75),
    (1, 5.0),
    (1, 5.25),
    (1, 5.5),
    (1, 5.75),
    (1, 6.0),
    (1, 6.25),
    (1, 6.5),
    (1, 6.75),
    (1, 7.0),
    (1, 7.25),
    (1, 7.5),
    (1, 7.75)
)



def get_target_offset(numerator):
    beat_types = {}
    beat_types[2] = [
        [0],
        [1],
        list(frange(0.5, 1, 1)),
        list(frange(0.25, 1, 0.5)),
    ]
    beat_types[4] = [
        [0],
        [2],
        [1, 3],
        list(frange(0.5, 3, 1)),
        list(frange(0.25, 3, 0.5)),
    ]
    beat_types[8] = [
        [0],
        [4],
        [2, 6],
        [1, 3, 5, 7],
        list(frange(0.5, 7, 1)),
        list(frange(0.25, 7, 0.5)),
    ]

    beat_type_weights = {}
    beat_type_weights[2] = scale_list([6, 5, 3, 1])
    beat_type_weights[4] = scale_list([7, 6, 5, 3, 1])
    beat_type_weights[8] = scale_list([8, 7, 6, 5, 3, 1])

    level = weighted_choice(beat_types[numerator], beat_type_weights[numerator])



    split_point = int(num_options * .75)
    a = level[:split_point]
    b = level[split_point:]


    numerator

    num_options = len(level)
    if num_options == 1:
        return level[0]
    elif num_options == 2:
        return random.choice(level)
    else:
        split_point = int(num_options * .75)
        a = level[:split_point]
        b = level[split_point:]
        if random.random() < 0.9:
            return random.choice(a)
        else:
            return random.choice(b)






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


# def choose_meter_duration():
#     durations = [8, 4, 2]
#     weights = [1, 8, 1]
#     return weighted_choice(durations, weights)

def choose_accents():



if __name__ == '__main__':
    main()
