from harmonic_rhythm import choose as choose_harmonic_rhythm
from form import choose as choose_form


def generate():
    form = choose_form()

    for bar_type in form.bar_types:
        bar_type.harmonic_rhythm = choose_harmonic_rhythm(bar.duration)

        # for harmony_duration in bar_type.harmonic_rhythm:
