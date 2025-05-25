"""Training tool: jamming with backing music."""

import os
import tkinter as tk
from tkinter import ttk

import numpy as np
import pyaudio
import pygame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.core.theory.chord import notes_to_chord
from src.core.theory.note import freq_to_note
from src.core.tune.noise_cancellation import bandpass_filter, dynamic_noise_gate

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
FORMAT = pyaudio.paFloat32


# ----- Tracks: store -----


pygame.mixer.init()

MUSIC_FOLDER = "data"
STYLE_FOLDER = "styles"
STYLE_TYPE_TO_NAME = {
    "jazz": "Jazz style",
    "blues": "Blues style",
    "rock": "Rock style",
    "pop": "Pop style",
    "country": "Country style",
    "folk": "Folk style",
    "latin": "Latin style",
    "reggae": "Reggae style",
}
STYLE_NAME_TO_TYPE = {v: k for k, v in STYLE_TYPE_TO_NAME.items()}


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Jamming")
root.geometry("700x620")

chord_var = tk.StringVar()
notes_var = tk.StringVar()
freqs_var = tk.StringVar()
status_var = tk.StringVar(value="Backing track stopped")


# ----- GUI: chord display -----


chord_frame = tk.Frame(root, bg=root["bg"])
chord_frame.pack(pady=10)

tk.Label(
    chord_frame, text="Detected chord", font=("Helvetica", 16), bg=root["bg"]
).pack(pady=5)
tk.Label(
    chord_frame, textvariable=chord_var, font=("Helvetica", 28, "bold"), bg=root["bg"]
).pack()
tk.Label(chord_frame, textvariable=notes_var, bg=root["bg"]).pack()
tk.Label(chord_frame, textvariable=freqs_var, bg=root["bg"]).pack()


# ----- GUI: separator -----


ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(20, 10))


# ----- GUI: controls -----


def play_track():
    track_name = track_var.get()
    style_name = style_var.get()
    style_type = STYLE_NAME_TO_TYPE.get(style_name)
    if style_type and track_name:
        pygame.mixer.music.load(
            os.path.join(MUSIC_FOLDER, STYLE_FOLDER, style_type, track_name)
        )
        pygame.mixer.music.play()
        status_var.set(f"Playing: {track_name}")
    else:
        status_var.set("Track not found")


def pause_track():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        status_var.set("Playback paused")


def unpause_track():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.unpause()
        status_var.set("Playback resumed")


def stop_track():
    pygame.mixer.music.stop()
    status_var.set("Backing track stopped")


def update_track(*args):
    style_name = style_var.get()
    style_type = STYLE_NAME_TO_TYPE.get(style_name)
    style_folder = (
        os.path.join(MUSIC_FOLDER, STYLE_FOLDER, style_type) if style_type else None
    )
    if not style_folder or not os.path.exists(style_folder):
        track_menu["values"] = []
        track_var.set("")
        return
    tracks = [
        file for file in os.listdir(style_folder) if file.endswith((".mp3", ".wav"))
    ]
    track_menu["values"] = tracks
    if tracks:
        track_var.set(tracks[0])
    else:
        track_var.set("")


controls_frame = tk.Frame(root, bg=root["bg"])
controls_frame.pack(pady=10)

tk.Label(controls_frame, text="Select style:", bg=root["bg"]).grid(
    row=0, column=0, padx=5, pady=5
)
style_var = tk.StringVar(value="Jazz style")
style_var.trace("w", update_track)
style_menu = ttk.Combobox(
    controls_frame,
    textvariable=style_var,
    values=list(STYLE_TYPE_TO_NAME.values()),
    state="readonly",
)
style_menu.grid(row=0, column=1, padx=5)

tk.Label(controls_frame, text="Select track:", bg=root["bg"]).grid(
    row=1, column=0, padx=5, pady=5
)
track_var = tk.StringVar(value="")
track_menu = ttk.Combobox(
    controls_frame,
    textvariable=track_var,
    state="readonly",
)
track_menu.grid(row=1, column=1, padx=5)

update_track()

tk.Button(controls_frame, text="Play", command=play_track).grid(row=2, column=0, padx=5)
tk.Button(controls_frame, text="Pause", command=pause_track).grid(
    row=2, column=1, padx=5
)
tk.Button(controls_frame, text="Resume", command=unpause_track).grid(
    row=2, column=2, padx=5
)
tk.Button(controls_frame, text="Stop", command=stop_track).grid(row=2, column=3, padx=5)

tk.Label(controls_frame, textvariable=status_var, bg=root["bg"]).grid(
    row=3, column=0, columnspan=4, pady=5
)


# ----- GUI: separator -----


ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)


# ----- GUI: audio waveform display -----


chart_frame = tk.Frame(root, bg=root["bg"], bd=1)
chart_frame.pack(pady=10)

tk.Label(
    chart_frame, text="Audio waveform", font=("Helvetica", 16), bg=root["bg"]
).pack()

fig = Figure(figsize=(6, 2.5), dpi=100)
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
