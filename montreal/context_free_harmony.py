from utils import weighted_choice

chord_types = [
    (0, 4, 7),
    (0, 3, 7),
    (0, 4, 7, 10),
    (0, 3, 7, 10),
    (0, 4, 7, 11),
    (0, 5, 7),
    (0, 7),
    (0, 5),
    (0, 4)
]

class Terminal(object):
    def __init__(self, value):
        self.type = 'terminal'
        self.value = value


class Expandable(object):
    def __init__(self, weights, options):
        self.type = 'expandable'
        self.weights = weights
        self.options = options

    def choose(self):
        choice = weighted_choice(self.options, self.weights)
        if choice.type == 'terminal':
            return choice.value
        else:
            return choice.choose()


tree = Expandable([.6, .4], [
    Terminal((0, 4, 7)),
    Expandable([.5, .4, .1], [
        Terminal((0, 3, 7)),
        Expandable([.6, .2, .1, .1], [
            Terminal((0, 4, 7, 10)),
            Terminal((0, 3, 7, 10)),
            Terminal((0, 4, 7, 11)),
            Terminal((0, 5, 7))
        ]),
        Expandable([.7, .2, .1], [
            Terminal((0, 7)),
            Terminal((0, 5)),
            Terminal((0, 4))
        ])
    ])
])


def choose():
    return tree.choose()
