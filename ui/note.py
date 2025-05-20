import tkinter as tk

import aubio
import numpy as np
import pyaudio

from tools.noise_cancellation import bandpass_filter, dynamic_noise_gate
from tools.note import freq_to_note

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
FORMAT = pyaudio.paFloat32


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Note Detector")
root.geometry("300x200")

note_var = tk.StringVar()
freq_var = tk.StringVar()
conf_var = tk.StringVar()

tk.Label(root, text="Detected note", font=("Helvetica", 16)).pack(pady=10)
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

    audio_data = bandpass_filter(audio_data, lowcut=80.0, highcut=1200.0)
    audio_data = audio_data.astype(np.float32)

    threshold_conf = pitch_detector.get_confidence()
    if threshold_conf > 0.85:
        threshold_gate = -60  # more permissive
    else:
        threshold_gate = -40  # stricter

    audio_data = dynamic_noise_gate(audio_data, threshold_db=threshold_gate)
    audio_data = audio_data.astype(np.float32)

    freq = pitch_detector(audio_data)[0]
    conf = pitch_detector.get_confidence()
    conf = max(0.0, min(conf, 1.0))

    note = freq_to_note(freq)

    if note:
        note_var.set(note)
        freq_var.set(f"Frequency: {freq:.1f} Hz")
        conf_var.set(f"Confidence: {conf:.2f}")
    else:
        note_var.set("—")
        freq_var.set("Frequency: —")
        conf_var.set("Confidence: —")

    root.after(50, update_pitch)


update_pitch()
root.mainloop()
