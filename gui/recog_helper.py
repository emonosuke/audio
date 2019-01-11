import numpy as np
import math

LIM_CEPSTRUM = 13


def get_spectrum(framed_w, sampling_rate):
    """
    Get spectrum of framed_w, using FFT
    """
    # fftSize = 2^p >= lenw
    fftSize = 1 << math.ceil(math.log2(len(framed_w)))
    fftSize2 = fftSize >> 1

    framed_w = [framed_w[i] if i < len(framed_w) else 0 for i in range(fftSize)]

    F = np.fft.fft(framed_w)
    absF = np.abs(F)
    spectrum = 20 * np.log10(absF)

    return spectrum[:fftSize2]


def get_cepstrum(waveform, sampling_rate, left, right):
    """
    Get cepstrum of a part of the waveform, using FFT of spectrum
    """
    framed_w = waveform[int(left):int(right)]

    # apply window function here
    hanningwindow = np.hanning(len(framed_w))
    framed_w = hanningwindow * framed_w

    spectrum = get_spectrum(framed_w, sampling_rate)

    F = np.fft.fft(spectrum)

    return F[:LIM_CEPSTRUM].real


def calc_likelihood(x, mean, std):
    """
    Likelihood is caluculated as follows
    
    - \sum_d (log(std_d) + (x_d - mean_d)^2 / (2 * std_d^2))

    (d = 0, 1, ..., LIM_CEPSTRUM(=13) - 1)
    """
    return (-1) * np.sum(np.log(std) + ((x - mean) ** 2) / (2 * (std ** 2)))
