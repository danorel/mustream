import tkinter as tk

import aubio
import numpy as np
import pyaudio

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
FORMAT = pyaudio.paFloat32


# ----- Tools: sound processing -----


def freq_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440.0
    semitones = int(round(12 * np.log2(freq / A4)))
    note_index = (semitones + 9) % 12
    octave = 4 + ((semitones + 9) // 12)
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{notes[note_index]}{octave}"


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Real-Time Note Detector")
root.geometry("300x200")

note_var = tk.StringVar()
freq_var = tk.StringVar()
conf_var = tk.StringVar()

tk.Label(root, text="Detected Note", font=("Helvetica", 16)).pack(pady=10)
tk.Label(root, textvariable=note_var, font=("Helvetica", 32, "bold")).pack()

tk.Label(root, textvariable=freq_var, font=("Helvetica", 12)).pack()
tk.Label(root, textvariable=conf_var, font=("Helvetica", 10)).pack()


# ----- Streaming: setup -----


p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=1,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=BUFFER_SIZE,
)
pitch_detector = aubio.pitch("default", BUFFER_SIZE * 2, BUFFER_SIZE, SAMPLE_RATE)
pitch_detector.set_unit("Hz")
pitch_detector.set_silence(-40)


# ----- Streaming: loop -----


def update_pitch():
    audio_data = np.frombuffer(
        stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32
    )
    pitch = pitch_detector(audio_data)[0]
    confidence = pitch_detector.get_confidence()

    note = freq_to_note(pitch)

    if note:
        note_var.set(note)
        freq_var.set(f"Freq: {pitch:.1f} Hz")
        conf_var.set(f"Confidence: {confidence:.2f}")
    else:
        note_var.set("—")
        freq_var.set("Freq: —")
        conf_var.set("Confidence: —")

    root.after(50, update_pitch)


update_pitch()
root.mainloop()
