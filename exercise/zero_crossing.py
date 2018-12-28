#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
各時間フレームごとに基本周波数を表示する
ただし、無声区間に対しては基本周波数は表示しない
"""

import sys
import math
import numpy as np
import scipy
import scipy.io.wavfile
import matplotlib.pyplot as plt
import pylab
import os
from autocorrelation import get_frequency

rootdir = os.path.dirname(os.getcwd())

DURATION = 0.2  # s
SHIFT = 0.1  # s


def get_zero_crossing(w):
    lenw = len(w)

    zero_crossed = 0

    for i in range(lenw - 1):
        if w[i] * w[i + 1] <= 0:
            zero_crossed += 1

    return zero_crossed / DURATION


def plot_voiced(waveform, sampling_rate):
    """
    基本周波数とゼロ交差数を比較して、有声音か無声音かを判定する
    さらに、有声音であれば基本周波数を spectrogram 上に重ねて表示する
    """
    left = 0
    right = DURATION * sampling_rate

    fqs = []

    # 各フレームごと
    while right < len(waveform):
        framed_w = waveform[int(left):int(right)]

        # 窓関数
        hanningwindow = np.hanning(len(framed_w))
        framed_w = hanningwindow * framed_w

        # 基本周波数を求める
        fq = get_frequency(framed_w, sampling_rate)

        # ゼロ交差数を求める
        zc = get_zero_crossing(framed_w)

        print('{:.1f} {:.1f} Frequency[Hz]: {:.2f} Zero Crossing[Hz]: {:.2f}'.format(
            left / sampling_rate, right / sampling_rate, fq, zc))

        # 無声音あるいは周波数が極端に大きい場合には基本周波数は0とする
        if fq <= 500 and zc <= fq * 10:
            fqs = np.append(fqs, fq)
        else:
            fqs = np.append(fqs, 0)

        left += SHIFT * sampling_rate
        right += SHIFT * sampling_rate

    # spectrogram の表示
    window_duration = 0.2
    window_shift = 0.1
    window_size = int(window_duration * sampling_rate)
    window_overlap = int((window_duration - window_shift) * sampling_rate)
    window = scipy.hanning(window_size)
    
    plt.title('Spectrogram & Frequency')

    sp, _, times, ax = plt.specgram(
        waveform,
        NFFT=window_size,
        Fs=sampling_rate,
        window=window,
        noverlap=window_overlap,
        cmap='hot',
        vmin=None,
        vmax=None
    )

    plt.colorbar()

    if len(times) > len(fqs):
        fqs = np.append(fqs, 0)
    
    plt.plot(times, fqs, color='red')
    plt.xlabel('Time [sec]')
    plt.ylabel('Frequency [Hz]')
    plt.ylim([0, 1000])

    plt.show()


if __name__ == '__main__':
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    # 各標本の値を-1から1の範囲に変換
    waveform = waveform / 32768.0

    plot_voiced(waveform, sampling_rate)
