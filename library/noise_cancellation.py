import numpy as np
from scipy.signal import butter, lfilter


def bandpass_butter(lowcut, highcut, fs, order=4):
    """Implements a bandpass filter using the Butterworth filter method. A bandpass filter allows only a certain range of frequencies to pass and attenuates frequencies outside that range.

    Args:
        lowcut: The lower frequency limit of the bandpass filter (e.g., 80 Hz).
        highcut: The upper frequency limit of the bandpass filter (e.g., 1200 Hz).
        fs: The sampling frequency of the audio data (e.g., 44100 Hz).
        order: The order of the filter (higher means sharper filtering).

    Returns:
        b: The numerator coefficients of the filter.
        a: The denominator coefficients of the filter.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def bandpass_filter(audio_data, lowcut=80.0, highcut=1200.0, fs=44100):
    """Keeps only frequencies between 'lowcut' Hz and 'highcut' Hz (typical for musical instruments).

    Analogy: If it’s not a musical instrument, assume it’s noise and silence it. (keep only mid-range sounds, like human voice or musical instruments; throw away very low / rumble sounds and very high / hiss sounds)

    Args:
        audio_data: The unprocessed audio data.
        lowcut: The lower frequency limit of the bandpass filter (e.g., 80 Hz).
        highcut: The upper frequency limit of the bandpass filter (e.g., 1200 Hz).
        fs: The sampling frequency of the audio data (e.g., 44100 Hz).

    Returns:
        audio_data: The processed audio data.
    """
    b, a = bandpass_butter(lowcut, highcut, fs)
    return lfilter(b, a, audio_data)


def dynamic_noise_gate(audio_data, threshold_db=-40):
    """Suppresses very quiet input below a certain decibel threshold (e.g., background noise).

    Analogy: If it’s whisper quiet, assume it’s noise and silence it.

    Args:
        audio_data: The unprocessed audio data.
        threshold_db: The decibel threshold below which the audio data is suppressed (e.g., -40 dB).

    Returns:
        audio_data: The processed audio data.
    """
    rms = np.sqrt(np.mean(audio_data**2))
    db = 20 * np.log10(rms + 1e-10)
    if db < threshold_db:
        return np.zeros_like(audio_data)
    return audio_data
