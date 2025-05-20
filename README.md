# mustream

**Toolbox for tech guys who are into guitar music**

This project provides real-time tools for detecting musical notes and chords through your microphone, with a simple UI for visualization. Perfect for musicians, music students, and developers interested in audio processing.

## Features

- 🎵 Real-time **note recognition** and **chord detection**
- 📊 Live **audio waveform plotting** for visual feedback

## Requirements

- Python 3.7 or higher
- PyAudio (for audio input)
- NumPy (for numerical computations)
- Matplotlib (for waveform visualization)
- Aubio (for pitch detection)
- SciPy (for signal processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/danorel/mustream.git
cd mustream
```

2. Create and activate a virtual environment (recommended)

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Before moving on, let's setup Python project folder:

```
export PYTHONPATH=.
```

The project provides three main applications:

### Note Detector

```bash
python ui/note.py
```

This will open a window showing:
- Frequency of sound
- Detected note

### Chord Detector

```bash
python ui/chord.py
```

This will open a window showing:
- Frequency of sound
- Detected chord
- Individual notes being played
- Live audio waveform visualization

### Jam

```bash
python ui/jam.py
```

This will open a window showing:
- Frequency of sound
- Detected chord
- Individual notes being played
- Live audio waveform visualization
- Music library
- Jam controls

## Development

The project uses several development tools to maintain code quality:
- `black` for code formatting
- `isort` for import sorting
- `flake`8 for linting
- `pre-commit` hooks for automated checks

To set up development tools:

```bash
pip install pre-commit
pre-commit install
```

## Contributing

Contributions and feature proposals are welcome! Please feel free to submit a PR.
