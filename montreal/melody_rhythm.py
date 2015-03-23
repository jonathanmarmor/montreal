from utils import S


rhythm_options = {}
rhythm_options[1] = S(
    # (15, [1]),
    # (25, [.5, .5]),
    (20, [.25, .75]),
    (28, [.75, .25]),
    (15, [.25, .25, .5]),
    (1, [.25, .5, .25]),
    (15, [.25, .25, .5]),
    (5, [.25, .25, .25, .25])
)
rhythm_options[2] = S(
    (5, rhythm_options[1].choose() + rhythm_options[1].choose()),
    (10, rhythm_options[1].choose() + [.25, .75]),
    (10, rhythm_options[1].choose() + [1.0]),
    (10, rhythm_options[1].choose() + [.5, .5]),
    # (3, [2]),
    # (5, [.25, 1.75]),
    # (15, [.5, 1.5]),
    # (15, [1.5, .5]),
    # (25, [1.75, .25]),
    # (5, [.25, .25, 1.5]),
    # (15, [1.5, .25, .25]),
    (5, [.75, .75, .5]),
    (5, [.5, .75, .75])
)
rhythm_options[4] = S(
    (10, rhythm_options[2].choose() + rhythm_options[2].choose()),
    (30, rhythm_options[2].choose() + rhythm_options[1].choose() + [.25, .75]),
    (30, rhythm_options[2].choose() + rhythm_options[1].choose() + [1.0]),
    (30, rhythm_options[2].choose() + rhythm_options[1].choose() + [.5, .5]),
    # (6, [4]),
    # (6, [.25, 3.75]),
    # (6, [.5, 3.5]),
    # (20, rhythm_options[1].choose() + [3]),
    # (3, [1.5, 2.5]),
    # (3, [2.5, 1.5]),
    # (5, [3] + rhythm_options[1].choose()),
    # (5, [3.5, .5]),
    # (5, [3.75, .25]),
    # (6, [.25, .25, 3.5]),
    # (6, [.5, .5, 3]),
    # (3, [1.5, 1.5, 1]),
    # (10, [1, 1.5, 1.5]),
    # (6, [3, .5, .5]),
    # (5, [3.5, .25, .25]),
    # (6, [.25, .25, .25, 3.25]),
    # (6, [3.25, .25, .25, .25]),
    # (3, [.25, .25, .5, 3]),
    # (3, [.5, .25, .25, 3]),
    # (13, [.25, .25, 1, 2.5]),
    # (3, [.25, .25, 2, 1.5]),
    # (13, [.25, .25, 3, .5]),
    # (13, [.5, .5, .25, 2.75]),
    # (19, [.5, .5, .5, 2.5]),
    # (17, [.5, .5, 1.5, 1.5]),
    # (12, [.5, .5, 2, 1]),
    # (3, [.5, .5, 2.5, .5]),
    # (7, [1, .75, .75, .75, .75]),
    # (7, [.75, .75, .75, .75, 1]),
)
rhythm_options[8] = S(
    (50, rhythm_options[4].choose() + rhythm_options[4].choose()),
    # (1, [8]),
    # (1, [7] + rhythm_options[1].choose()),
    # (1, rhythm_options[1].choose() + [7]),
    # (1, [6] + rhythm_options[2].choose()),
    # (1, rhythm_options[2].choose() + [6]),
)


def get_melody_rhythm(n):
    return rhythm_options[n].choose()
