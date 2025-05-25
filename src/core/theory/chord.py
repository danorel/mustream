CHORDS = {
    "A minor": {"A", "C", "E"},
    "A major": {"A", "C#", "E"},
    "B minor": {"B", "D", "F#"},
    "B major": {"B", "D#", "F#"},
    "C minor": {"C", "Eb", "G"},
    "C major": {"C", "E", "G"},
    "D minor": {"D", "F", "A"},
    "D major": {"D", "F#", "A"},
    "E minor": {"E", "G", "B"},
    "E major": {"E", "G#", "B"},
    "F major": {"F", "A", "C"},
    "F minor": {"F", "Ab", "C"},
    "G major": {"G", "B", "D"},
    "G minor": {"G", "Bb", "D"},
    "G# major": {"G#", "B#", "D#"},
    "G# minor": {"G#", "B", "D#"},
}


def notes_to_chord(notes):
    stripped_notes = {note[:-1] for note in notes}
    for chord, required in CHORDS.items():
        if required.issubset(stripped_notes):
            return chord
    return None
