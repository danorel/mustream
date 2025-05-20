import numpy as np


def freq_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440.0
    semitones = int(round(12 * np.log2(freq / A4)))
    note_index = (semitones + 9) % 12
    octave = 4 + ((semitones + 9) // 12)
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{notes[note_index]}{octave}"
