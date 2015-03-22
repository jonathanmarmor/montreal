import random


class Form(object):
    def __init__(self, form_string):
        form_string = form_string.strip().replace(' ', '')
        self.form_string = form_string
        self.bars = []
        self.bar_types = {}
        for char in form_string:
            if char != '-':
                b = Bar(char)
                self.bars.append(b)
            else:
                b.duration += 2

        for bar in self.bars:
            if bar.type not in self.bar_types:
                self.bar_types[bar.type] = BarType(bar.type, bar.duration)
            bar.type_obj = self.bar_types[bar.type]

        self.duration = sum([b.duration for b in self.bars])

    def __repr__(self):
        return self.form_string
        # return ' '.join([str(b) for b in self.bars])


class Bar(object):
    def __init__(self, bar_type):
        self.type = bar_type
        self.duration = 2
        self.tempo = None

    def __repr__(self):
        return '{}{}'.format(self.type, self.duration)


class BarType(object):
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

        names = [
            'ob',
            'cl',
            'fl',
            'sax',
            'tpt',
            'vln',
            'vib',
            'bs'
        ]
        self.parts = [{'instrument_name': n, 'notes': []} for n in names]


def parse_file():
    filename = '/Users/jmarmor/repos/jonathanmarmor/montreal/montreal/forms.txt'
    return [Form(line) for line in open(filename)]


FORMS = parse_file()


def choose():
    return random.choice(FORMS)


if __name__ == '__main__':
    f = choose()
    for b in f.bars:
        print b.type_obj.harmonic_rhythm