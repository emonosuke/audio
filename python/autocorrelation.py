#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
短時間フレームごとの基本周波数を自己相関を用いて推定する
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
import math

rootdir = os.path.dirname(os.getcwd())

frameDuration = 0.2
frameShift = 0.1


def autocorr(x, t):
    N = len(x)
    S = 0
    for i in range(N - t):
        S += x[i] * x[i + t]
    return S


def get_frequency(w):
    lenw = len(w)
    maxac = -10000.0
    # 対応する基本周波数
    ff = 0

    flagFirst = True  # はじめのピークにいる場合True

    pa = autocorr(w, 0)
    # print(pa) # t = 0 で自己相関は最大
    for i in range(1, lenw // 2):
        a = autocorr(w, i)
        if flagFirst:
            if pa < a: 
                flagFirst = False
        else:
            if maxac < a:
                ff = 1.0 / (i / sampling_rate)
                maxac = a
        pa = a
    
    return ff


def plot_frequencies(waveform, sampling_rate):
    left = 0
    right = frameDuration * sampling_rate

    ffs = []
    times = []
    while right < len(waveform):
        # print(left, right)
        ff = get_frequency(waveform[int(left):int(right)])
        ffs.append(ff)
        
        mid = (left + right) / 2
        times.append(mid / sampling_rate)

        left += frameShift * sampling_rate
        right += frameShift * sampling_rate

        print('{:.2f} {:.2f} Frequency[Hz]: {:.2f}'.format(left / sampling_rate, right / sampling_rate, ff))

    plt.plot(times, ffs)
    plt.title('Fundamental Frequency')
    plt.xlabel('Time [sec]')
    plt.ylabel('Frequency [Hz]')
    plt.show()

if __name__ == '__main__':
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    waveform = waveform / 32768.0

    plot_frequencies(waveform, sampling_rate)
