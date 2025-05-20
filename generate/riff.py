import random

from music21 import duration, meter, note, scale, stream


def generate(key="C", scale_type="major", length=8):
    sc = scale.MajorScale(key) if scale_type == "major" else scale.MinorScale(key)

    riff_stream = stream.Stream()
    riff_stream.append(meter.TimeSignature("4/4"))

    for _ in range(length):
        pitch = random.choice(sc.getPitches())
        n = note.Note(pitch)
        n.duration = duration.Duration(random.choice([0.25, 0.5, 1]))
        riff_stream.append(n)

    return riff_stream


if __name__ == "__main__":
    riff = generate("C", "major", 16)
    riff.show("midi")
