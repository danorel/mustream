import time
import tkinter as tk
from tkinter import ttk

import aubio
import numpy as np
import pyaudio
import pygame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import butter, lfilter

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100

FORMAT = pyaudio.paFloat32

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

PLOT_UPDATE_LAST_TIMESTAMP = 0
PLOT_UPDATE_INTERVAL = 0.5


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


def detect_chord(notes):
    stripped_notes = {n[:-1] for n in notes}
    for chord, required in CHORDS.items():
        if required.issubset(stripped_notes):
            return chord
    return None


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def bandpass_filter(data, lowcut=80.0, highcut=1200.0, fs=SAMPLE_RATE):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return lfilter(b, a, data)


def dynamic_noise_gate(data, threshold_db=-40):
    rms = np.sqrt(np.mean(data**2))
    db = 20 * np.log10(rms + 1e-10)
    if db < threshold_db:
        return np.zeros_like(data)
    return data


# ----- Library: music store -----

pygame.mixer.init()

BACKING_LIBRARY_FOLDER = "library"

BACKING_TRACKS = {
    "Jazz Style": f"{BACKING_LIBRARY_FOLDER}/backing_jazz.wav",
}


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Jamming")
root.geometry("720x540")

note_var = tk.StringVar()
freq_var = tk.StringVar()
conf_var = tk.StringVar()
status_var = tk.StringVar(value="Backing track stopped")


# ----- GUI: chord display -----


chord_frame = tk.Frame(root, bg=root["bg"])
chord_frame.pack(pady=10)

tk.Label(
    chord_frame, text="Detected Chord", font=("Helvetica", 16), bg=root["bg"]
).pack(pady=5)
tk.Label(
    chord_frame, textvariable=note_var, font=("Helvetica", 28, "bold"), bg=root["bg"]
).pack()
tk.Label(chord_frame, textvariable=freq_var, bg=root["bg"]).pack()
tk.Label(chord_frame, textvariable=conf_var, bg=root["bg"]).pack()


# ----- GUI: separator -----


ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)


# ----- GUI: controls -----


def play_track():
    track_name = style_var.get()
    track_path = BACKING_TRACKS.get(track_name)
    if track_path:
        pygame.mixer.music.load(track_path)
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


controls_frame = tk.Frame(root, bg=root["bg"])
controls_frame.pack(pady=10)

tk.Label(controls_frame, text="Select Style:", bg=root["bg"]).grid(
    row=0, column=0, padx=5
)
style_var = tk.StringVar(value="Jazz Style")
style_menu = ttk.Combobox(
    controls_frame,
    textvariable=style_var,
    values=list(BACKING_TRACKS.keys()),
    state="readonly",
)
style_menu.grid(row=0, column=1, padx=5)

tk.Button(controls_frame, text="Play", command=play_track).grid(row=0, column=2, padx=5)
tk.Button(controls_frame, text="Pause", command=pause_track).grid(
    row=0, column=3, padx=5
)
tk.Button(controls_frame, text="Resume", command=unpause_track).grid(
    row=0, column=4, padx=5
)
tk.Button(controls_frame, text="Stop", command=stop_track).grid(row=0, column=5, padx=5)

tk.Label(controls_frame, textvariable=status_var, bg=root["bg"]).grid(
    row=1, column=0, columnspan=6, pady=5
)

# ----- GUI: separator -----


ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)


# ----- GUI: audio waveform display -----


chart_frame = tk.Frame(root, bg=root["bg"], bd=1)
chart_frame.pack(pady=10)

tk.Label(
    chart_frame, text="Audio Waveform", font=("Helvetica", 16), bg=root["bg"]
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
pitch_detector = aubio.pitch("default", BUFFER_SIZE * 2, BUFFER_SIZE, SAMPLE_RATE)
pitch_detector.set_unit("Hz")
pitch_detector.set_silence(-40)


# ----- Streaming: loop -----


def update_pitch():
    global PLOT_UPDATE_LAST_TIMESTAMP
    current_timestamp = time.time()

    audio_data = np.frombuffer(
        stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32
    )
    audio_data = bandpass_filter(audio_data, lowcut=80.0, highcut=1200.0)
    audio_data = dynamic_noise_gate(audio_data, threshold_db=-40)

    spectrum = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(spectrum), 1 / SAMPLE_RATE)
    magnitude = np.abs(spectrum)

    idx = np.where((freqs > 60) & (freqs < 2000))
    freqs = freqs[idx]
    magnitude = magnitude[idx]

    top_indices = np.argsort(magnitude)[-6:]
    dominant_freqs = freqs[top_indices]
    dominant_freqs.sort()

    notes = []
    for f in dominant_freqs:
        note = freq_to_note(f)
        if note and note[:-1] not in [n[:-1] for n in notes]:
            notes.append(note)

    detected_chord = detect_chord(notes)

    note_var.set(detected_chord if detected_chord else "Unknown")
    freq_var.set(f"Notes: {', '.join(notes)}")
    conf_var.set(f"Top Freqs: {', '.join(f'{f:.1f}' for f in dominant_freqs)}")

    if current_timestamp - PLOT_UPDATE_LAST_TIMESTAMP >= PLOT_UPDATE_INTERVAL:
        ax.clear()
        ax.plot(audio_data)
        ax.set_ylim(-0.5, 0.5)
        ax.set_title("Live Audio Waveform")
        canvas.draw()
        PLOT_UPDATE_LAST_TIMESTAMP = current_timestamp

    root.after(200, update_pitch)


if __name__ == "__main__":
    update_pitch()
    root.mainloop()
