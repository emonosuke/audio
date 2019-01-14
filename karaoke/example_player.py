import sys
import math
import numpy as np
import scipy
import scipy.io.wavfile
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation
import time
import sounddevice as sd
import soundfile as sf

FRAME_DURATION = 0.2
FRAME_SHIFT = 0.1
now = 0


def calc_specgram(waveform, sampling_rate):
    """
    Set specgrams
    """
    global specgram

    left = 0
    right = FRAME_DURATION * sampling_rate

    while right < len(waveform):
        wframe = waveform[int(left):int(right)]

        hanningwindow = np.hanning(len(wframe))
        wframe = hanningwindow * wframe

        specgram.append(np.log(np.abs(np.fft.rfft(wframe))))

        left += FRAME_SHIFT * sampling_rate
        right += FRAME_SHIFT * sampling_rate


def updatefig(*args):
    global specgram
    global target_spec
    global start
    global now

    elapsed = time.time() - start
    # print(elapsed)
    if elapsed >= (now + 1) * FRAME_SHIFT:
        now += 1
        if now >= len(specgram):
            print("end of music")
            sys.exit(0)

    target_spec[0] = specgram[now]
    target_spec = np.roll(target_spec, -1, axis=0)

    im.set_array(np.transpose(target_spec))

    return im,


if __name__ == '__main__':
    sampling_rate, waveform = scipy.io.wavfile.read(sys.argv[1])
    waveform = waveform / 32768.0

    specgram = []

    calc_specgram(waveform, sampling_rate)

    nyquist = sampling_rate / 2

    # initialize spectrogram
    fig, ax = plt.subplots()

    lenfreq = (int(sampling_rate * FRAME_DURATION) >> 1) + 1
    target_spec = np.zeros([20, lenfreq])
    
    extent = [0.0, 1.0, 0.0, nyquist]

    im = plt.imshow(np.transpose(specgram), cmap='hot', origin='lower', aspect='auto', extent=extent)

    # play music background
    data, fs = sf.read(sys.argv[1], dtype='float32')
    print(fs)
    print(data[:20])
    print(waveform[:20])
    sd.play(data, fs)

    start = time.time()

    ani = FuncAnimation(fig, updatefig, interval=1, blit=True)
    
    plt.show()
