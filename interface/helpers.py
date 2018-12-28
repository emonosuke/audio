import numpy as np
import math

FRAME_DURATION = 0.2
FRAME_SHIFT = 0.1
LIM_FREQ = 500
ZERO_CROSSING_RATE = 10


def autocorr(x, t):
    N = len(x)

    return np.dot(x[:N-t], x[t:N])


def fundamental_by_frame(framed_w, sampling_rate):
    """
    For each frame, predict Fundamental frequency.
    """
    ff = 0

    firstpeak = True

    prev_corr = autocorr(framed_w, 0)

    for i in range(1, len(framed_w) // 2):
        corr = autocorr(framed_w, i)

        if firstpeak:
            if prev_corr <= corr:
                firstpeak = False
                max_corr = corr
        else:
            if max_corr <= corr:
                ff = 1.0 / ((i - 1) / sampling_rate)
                max_corr = corr
        prev_corr = corr
    
    return ff


def zero_crossing(framed_w):
    zero_crossed = 0

    for i in range(len(framed_w) - 1):
        if framed_w[i] * framed_w[i + 1] <= 0:
            zero_crossed += 1
    
    return zero_crossed / FRAME_DURATION


def predict_fundamentals(waveform, sampling_rate):
    """
    Split waveform into frames, 
    """
    left = 0
    right = FRAME_DURATION * sampling_rate

    fundamentals = []

    while right < len(waveform):
        framed_w = waveform[int(left):int(right)]

        # apply window function
        hanningwindow = np.hanning(len(framed_w))
        framed_w = hanningwindow * framed_w

        fbf = fundamental_by_frame(framed_w, sampling_rate)

        zc = zero_crossing(framed_w)

        if fbf <= LIM_FREQ and zc <= fbf * ZERO_CROSSING_RATE:
            fundamentals = np.append(fundamentals, fbf)
        else:
            fundamentals = np.append(fundamentals, math.nan)

        left += FRAME_SHIFT * sampling_rate
        right += FRAME_SHIFT * sampling_rate 

    return fundamentals
