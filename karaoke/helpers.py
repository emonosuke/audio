import numpy as np
import math

EPS = 1e-6


def autocorr(x, t):
    """
    Autocorrelation between x and t-shifted x
    """
    N = len(x)

    return np.dot(x[:N-t], x[t:N])


def get_frequency(wframe, samplerate):
    """
    For each frame, predict Fundamental frequency.
    """
    ff = 0

    firstpeak = True

    prev_corr = autocorr(wframe, 0)

    for i in range(1, len(wframe) // 2):
        corr = autocorr(wframe, i)

        if firstpeak:
            if prev_corr <= corr:
                firstpeak = False
                max_corr = corr
        else:
            if max_corr <= corr:
                ff = 1.0 / ((i - 1) / samplerate)
                max_corr = corr
        prev_corr = corr
    
    return ff


def get_loudness(wframe):
    """
    For each frame, get volume
    """
    rms = np.sqrt(np.sum(wframe ** 2) / len(wframe))
    vol = 20 * math.log10(rms + EPS)
    return vol
