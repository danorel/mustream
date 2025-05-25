# mustream


**Toolbox for tech guys who are into music and more**

This project provides real-time tools for learning musical theory with accompanying visualization plugins through your microphone with set of simple UI applications. Perfect for musicians, music students, and developers interested in audio understanding and processing.


## Features


- 📏 Measurement tools: **decibel meter**
- 🎵 Real-time detection tools: **note recognition** and **chord detection**
- 📊 Training tools: live **jamming** with backing music


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

```commandline
export PYTHONPATH=.
```

The project provides set of musical applications:


### Measurement tools


#### Decibel meter

Decibel meter tool, which supports monophonic voice or instrument, analysing sound level.

```bash
python src/ui/tool/measurer/decibel_meter.py
```

This will open a window showing:
- Frequency of sound
- Detected note
- Live decibel visualization


### Detection tools


#### Note detector

Note detection tool, which supports monophonic voice or instrument playing single dominant tone.

```bash
python src/ui/tool/detector/note.py
```

This will open a window showing:
- Frequency of sound
- Detected note


#### Chord detector

Chord detection tool, which supports monophonic voice or instrument playing multiple dominant tones or harmonics.

```bash
python src/ui/tool/detector/chord.py
```

This will open a window showing:
- Frequency of sound
- Detected chord
- Individual notes being played
- Live audio waveform visualization


### Training tools


#### Jam

Jamming with backing jazz music.

```bash
python src/ui/training/jam.py
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
