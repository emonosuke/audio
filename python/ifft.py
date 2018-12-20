import sys
import os
import scipy.io.wavfile
import numpy as np

rootdir = os.path.dirname(os.getcwd())

if __name__ == '__main__':
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    print('length of waveform: ', len(waveform))
    print('sampling_rate: ', sampling_rate)

    left_t = 0
    right_t = len(waveform)

    if len(sys.argv) >= 3:
        left_t = float(sys.argv[2])
    if len(sys.argv) >= 4:
        right_t = float(sys.argv[3])

    left = int(left_t * sampling_rate)
    right = int(right_t * sampling_rate)

    waveform = waveform / 32768.0

    F = np.fft.fft(waveform)

    print(F[:13].real)

    lenF = len(F)

    print(F[(lenF - 13):].real)

    f = np.fft.ifft(F)
    