import pyaudio
import numpy as np
import aubio
import time

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
    if freq <= 0: return None
    semitones = int(round(12 * np.log2(freq / A4)))
    note_index = (semitones + 9) % 12
    octave = 4 + ((semitones + 9) // 12)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    return f"{notes[note_index]}{octave}"

# Real-time loop
print("🎵 Listening... Play a note!")

last_note = None
note_stable_count = 0

try:
    while True:
        audio_data = np.frombuffer(stream.read(BUFFER_SIZE, exception_on_overflow=False), dtype=np.float32)
        pitch = pitch_detector(audio_data)[0]
        note = freq_to_note(pitch)

        # Print note only if it is stable for a few frames
        if note and note != last_note:
            last_note = note
            note_stable_count = 1
        elif note == last_note:
            note_stable_count += 1

        if note and note_stable_count == 3:
            print(f"🎶 Note Detected: {note}")
            note_stable_count = 0  # Reset so it prints again if note remains

except KeyboardInterrupt:
    print("\n🎤 Stopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()
