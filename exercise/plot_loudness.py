#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
import math

rootdir = os.path.dirname(os.getcwd())

frameDuration = 0.2
frameShift = 0.2 / 8.0


def plot_waveform(waveform, sampling_rate):
    left = 0
    right = frameDuration * sampling_rate
    # print(left, right)
    # 各フレーム([left, right))に対する音量(dB)のリスト
    dBs = []
    times = []
    while right < len(waveform):
        N = right - left
        # RMS
        S = 0
        for i in range(int(left), int(right)):
            S += waveform[i] ** 2
        # print(S, N)
        RMS = math.sqrt(S / N)
        dB = 20 * math.log10(RMS)
        dBs.append(dB)
        
        mid = (left + right) / 2
        times.append(mid / sampling_rate)

        left += frameShift * sampling_rate
        right += frameShift * sampling_rate

    # print(dBs)

    plt.plot(times, dBs)
    plt.title('Loudness')
    plt.xlabel('Time [sec]')
    plt.ylabel('Loudness [dB]')
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('no input files')
        sys.exit(1)

    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    print('sample rate of wav file: ', sampling_rate)
    print(waveform)

    # 各標本の値を-1から1の範囲に変換
    # waveform = waveform / 32768.0
    plot_waveform(waveform, sampling_rate)