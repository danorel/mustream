"""Detection tool: chord detector supporting monophonic voice or instrument playing multiple dominant tones or harmonics."""

import tkinter as tk
from tkinter import ttk

import aubio
import numpy as np
import pyaudio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.core.theory.chord import notes_to_chord
from src.core.theory.note import freq_to_note
from src.core.tune.noise_cancellation import bandpass_filter, dynamic_noise_gate

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
FORMAT = pyaudio.paFloat32


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Chord detector")
root.geometry("480x440")

chord_var = tk.StringVar()
notes_var = tk.StringVar()
freqs_var = tk.StringVar()


# ----- GUI: chord display -----


chord_frame = tk.Frame(root, bg=root["bg"])
chord_frame.pack(pady=10)

tk.Label(
    chord_frame, text="Detected chord", font=("Helvetica", 16), bg=root["bg"]
).pack(pady=5)
tk.Label(
    chord_frame, textvariable=chord_var, font=("Helvetica", 24, "bold"), bg=root["bg"]
).pack()
tk.Label(chord_frame, textvariable=notes_var, bg=root["bg"]).pack()
tk.Label(chord_frame, textvariable=freqs_var, bg=root["bg"]).pack()


# ----- GUI: separator -----


separator = ttk.Separator(root, orient="horizontal")
separator.pack(fill="x", pady=10)


# ----- GUI: audio waveform display -----


chart_frame = tk.Frame(root, bg=root["bg"], bd=1)
chart_frame.pack(pady=10)

tk.Label(
    chart_frame, text="Audio waveform", font=("Helvetica", 16), bg=root["bg"]
).pack()

fig = Figure(figsize=(5, 2), dpi=100)
fig.patch.set_alpha(0.0)
ax = fig.add_subplot(111)
ax.set_facecolor((0, 0, 0, 0))

canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().configure(bg=root["bg"], highlightthickness=0, bd=0)
canvas.get_tk_widget().pack()


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


# ----- Streaming: loop -----


def update_pitch():
    audio_data = np.frombuffer(
        stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32
    )
    audio_data = bandpass_filter(audio_data, lowcut=80.0, highcut=1200.0)
    audio_data = dynamic_noise_gate(audio_data, threshold_db=-40)
    audio_data = np.ascontiguousarray(audio_data, dtype=np.float32)

    spectrum = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(spectrum), 1 / SAMPLE_RATE)
    magnitude = np.abs(spectrum)

    idx = np.where((freqs > 60) & (freqs < 1200))
    magnitude = magnitude[idx]

    top_indices = np.argsort(magnitude)[-6:]
    dominant_freqs = freqs[idx][top_indices]
    dominant_freqs.sort()

    notes = []
    for freq in dominant_freqs:
        note = freq_to_note(freq)
        if note and note[:-1] not in [n[:-1] for n in notes]:
            notes.append(note)

    detected_chord = notes_to_chord(notes)

    chord_var.set(detected_chord if detected_chord else "Unknown")
    notes_var.set(f"Notes: {', '.join(notes)}")
    freqs_var.set(
        f"Top frequencies: {', '.join(f'{freq:.1f}' for freq in dominant_freqs)}"
    )

    ax.clear()
    ax.plot(audio_data)
    ax.set_ylim(-0.5, 0.5)
    canvas.draw()

    root.after(ms=50, func=update_pitch)


if __name__ == "__main__":
    update_pitch()
    root.mainloop()
