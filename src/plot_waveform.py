#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
import soundfile as sf

root_dir = os.path.dirname(os.getcwd())


def plot_waveform(waveform, sampling_rate):
    print(waveform)
    times = np.arange(len(waveform)) / sampling_rate
    plt.plot(times, waveform, linewidth=0.5, color='darkorange')
    plt.title('Waveform')
    plt.xlabel('Time [sec]')
    plt.ylabel('Amplitude')
    plt.xlim([0, len(waveform) / sampling_rate])
    plt.ylim([-1, 1])
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('no input files')
        sys.exit(1)

    filename = os.path.join(root_dir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    print('sample rate of wav file: ', sampling_rate)
    print(np.min(waveform) / 32768.0, np.max(waveform) / 32768.0)

    # 各標本の値を-1から1の範囲に変換
    waveform = waveform / 32768.0
    plot_waveform(waveform, sampling_rate)
