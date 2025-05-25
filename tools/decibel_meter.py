import tkinter as tk

import aubio
import numpy as np
import pyaudio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from library.note import freq_to_note

# ----- Constants -----


BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
FORMAT = pyaudio.paFloat32


# ----- GUI -----


root = tk.Tk()
root.title("🎵 Decibel Meter")
root.geometry("520x400")

note_var = tk.StringVar()
freq_var = tk.StringVar()
conf_var = tk.StringVar()

tk.Label(root, text="Detected note", font=("Helvetica", 16)).pack(pady=10)
tk.Label(root, textvariable=note_var, font=("Helvetica", 32, "bold")).pack()
tk.Label(root, textvariable=freq_var, font=("Helvetica", 12)).pack()
tk.Label(root, textvariable=conf_var, font=("Helvetica", 10)).pack()


# ----- GUI: volume plot -----


chart_frame = tk.Frame(root, bg=root["bg"], bd=1)
chart_frame.pack(pady=10)

fig = Figure(figsize=(5, 2), dpi=100)
fig.patch.set_alpha(0.0)
ax = fig.add_subplot(111)
ax.set_facecolor((0, 0, 0, 0))

bar = ax.bar([""], [-100], color="#4CAF50", width=0.4)
ax.set_ylim(-120, 0)
ax.set_yticks([-120, -100, -80, -60, -40, -20, 0])
ax.set_yticklabels(["-120", "-100", "-80", "-60", "-40", "-20", "0"], fontsize=8)
ax.set_xticks([])
ax.set_ylabel("dB")
ax.set_title("Volume level", fontsize=10, pad=5)
ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.5)
fig.tight_layout()
fig.subplots_adjust(right=0.88)

canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().configure(bg=root["bg"], highlightthickness=0, bd=0)
canvas.get_tk_widget().pack(anchor="center")


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


# ----- Tools: decibel conversion -----


def rms_to_db(audio_data):
    rms = np.sqrt(np.mean(audio_data**2))
    db = 20 * np.log10(rms + 1e-10)
    return db


# ----- Main Loop -----


def update_pitch():
    audio_data = np.frombuffer(
        stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32
    )

    freq = pitch_detector(audio_data)[0]
    conf = pitch_detector.get_confidence()
    note = freq_to_note(freq)

    if note:
        note_var.set(note)
        freq_var.set(f"Frequency: {freq:.1f} Hz")
        conf_var.set(f"Confidence: {conf:.2f}")
    else:
        note_var.set("—")
        freq_var.set("Frequency: —")
        conf_var.set("Confidence: —")

    db = rms_to_db(audio_data)
    bar[0].set_height(db)
    canvas.draw()

    root.after(50, update_pitch)


update_pitch()
root.mainloop()
