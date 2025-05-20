import numpy as np
from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def bandpass_filter(data, lowcut=80.0, highcut=1200.0, fs=44100):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return lfilter(b, a, data)


def dynamic_noise_gate(data, threshold_db=-40):
    rms = np.sqrt(np.mean(data**2))
    db = 20 * np.log10(rms + 1e-10)
    if db < threshold_db:
        return np.zeros_like(data)
    return data
