import pyaudio
import numpy as np
import aubio
import time
from collections import Counter

# Constants
BUFFER_SIZE = 8192
SAMPLE_RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paFloat32

# Setup
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=BUFFER_SIZE)

# Initialize pitch detection
pitch_detector = aubio.pitch("default", BUFFER_SIZE*2, BUFFER_SIZE, SAMPLE_RATE)
pitch_detector.set_unit("Hz")
pitch_detector.set_silence(-40)

# Frequency to note
def freq_to_note(freq):
    A4 = 440.0
    if freq == 0: return None
    semitones = int(round(12 * np.log2(freq / A4)))
    note_index = (semitones + 9) % 12
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes[note_index]

# Very simple chord matcher
def identify_chord(notes):
    note_set = set(notes)
    chords = {
        frozenset(['C', 'E', 'G']): 'C Major',
        frozenset(['A', 'C', 'E']): 'A minor',
        frozenset(['D', 'F#', 'A']): 'D Major',
        frozenset(['E', 'G#', 'B']): 'E Major',
        frozenset(['G', 'B', 'D']): 'G Major',
        frozenset(['F', 'A', 'C']): 'F Major',
        frozenset(['D', 'F', 'A']): 'D minor',
        frozenset(['E', 'G', 'B']): 'E minor',
        frozenset(['G', 'Bb', 'D']): 'G minor',
    }
    for chord_notes, name in chords.items():
        if chord_notes.issubset(note_set):
            return name
    return "Unknown"

# Real-time loop
print("🎸 Listening... Play a chord on your guitar!")

try:
    detected_notes = []

    while True:
        audio_data = np.frombuffer(stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32)
        pitch = pitch_detector(audio_data)[0]

        note = freq_to_note(pitch)
        if note:
            detected_notes.append(note)

        # Process every 1 second
        if len(detected_notes) > 20:
            most_common_notes = [n for n, _ in Counter(detected_notes).most_common(3)]
            chord = identify_chord(most_common_notes)
            print(f"🎶 Chord Detected: {chord}  | Notes: {most_common_notes}")
            detected_notes = []
            time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🎤 Stopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()