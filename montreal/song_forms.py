import itertools

from utils import weighted_choice


def validate(array):
    # Remove boring ones
    uniques = set(array)
    len_uniques = len(uniques)
    if len_uniques < 3:
        return False
    # Remove overly interesting ones
    if len_uniques > 5:
        return False
    # Remove illegal ones
    for index, item in enumerate(array[1:]):
        if item not in array[:index + 1] and item - 1 not in array[:index + 1]:
            return False

    # Remove ones where 0 isn't repeated after 1 happens, 1 isn't repeated after 2 happens,
    # 2 isn't repeated after 3 happens, or 3 isn't repeated after 4 happens
    uniques = list(uniques)
    uniques.sort()
    good = any(a in array[array.index(b) + 1:] for a, b in zip(uniques[:-1], uniques[1:]))
    if not good:
        return False

    return True


def get_forms(n):
    args = [range(i + 1) for i in range(n)]
    product = itertools.product(*args)
    return filter(validate, product)


def build_form_weights_4():
    weights = [8, 1, 8, 1]
    forms = [(0, 1, 0, 2), (0, 1, 2, 0), (0, 1, 2, 1), (0, 1, 0)]
    return forms, weights


def build_form_weights(n):
    weights = []
    forms = get_forms(n)
    for form in forms:
        if form[:4] == (0, 1, 2, 0):
            weights.append(1)
        if form[:4] == (0, 1, 2, 3):
            weights.append(1)
        else:
            weights.append(8)
    return forms, weights


def build_group_weights():
    weights = [11, 3, 5, 2, 9, 1]
    options = [
        build_form_weights_4(),
        build_form_weights(5),
        build_form_weights(6),
        build_form_weights(7),
        build_form_weights(8),
        build_form_weights(9)
    ]
    return options, weights


GROUP_OPTIONS, GROUP_WEIGHTS = build_group_weights()


def choose():
    try:  # TODO HOLY SHIT REMOVE THIS. infinite loop danger. find actual bug.
        forms, weights = weighted_choice(GROUP_OPTIONS, GROUP_WEIGHTS)
        return weighted_choice(forms, weights)
    except:
        print 'warning!  song_forms.choose failed and retried.'
        return choose()

