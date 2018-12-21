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

    return np.dot(np.array(x[:N-t]), np.array(x[t:N]))


def get_frequency(w, sr):
    """
    与えられた波形範囲の基本周波数を求める
    """
    lenw = len(w)

    # 対応する基本周波数
    ff = 0

    # 2番目に大きいピークが基本周波数に対応する
    firstpeak = True  # はじめのピークにいる場合True

    # 直前の自己相関の値
    prev = autocorr(w, 0)

    for i in range(1, lenw // 2):
        corr = autocorr(w, i)
        if firstpeak:
            # はじめのピークを抜ける
            if prev <= corr:
                firstpeak = False
                maxcorr = corr
        else:
            if maxcorr <= corr:
                ff = 1.0 / ((i - 1) / sr)
                maxcorr = corr
        prev = corr
    
    return ff


def plot_frequencies(waveform, sampling_rate):
    left = 0
    right = frameDuration * sampling_rate

    ffs = []
    times = []
    while right < len(waveform):
        framed_w = waveform[int(left):int(right)]

        # 窓関数
        hanningwindow = np.hanning(len(framed_w))
        framed_w = hanningwindow * framed_w

        ff = get_frequency(framed_w, sampling_rate)
        ffs.append(ff)
        
        mid = (left + right) / 2
        times.append(mid / sampling_rate)

        print('{:.2f} {:.2f} Frequency[Hz]: {:.2f}'.format(left / sampling_rate, right / sampling_rate, ff))

        left += frameShift * sampling_rate
        right += frameShift * sampling_rate

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
