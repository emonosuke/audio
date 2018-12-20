#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
./plot_spectrum.py wavfile left[sec] right[sec]
left[sec] と right[sec] 間の spectrum を表示
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
import math

rootdir = os.path.dirname(os.getcwd())


def plot_spectrum(w, sampling_rate):
    lenw = len(w)

    # fftSize = 2^p >= lenw を満たす fftSize を求める
    fftSize = 1 << math.ceil(math.log2(lenw))
    fftSize2 = (fftSize >> 1) + 1

    # 信号長を fftSize に伸ばし、足りない部分は0で埋める
    w = [w[i] if i < lenw else 0 for i in range(fftSize)]

    # 高速フーリエ変換
    F = np.fft.fft(w)
    absF = np.abs(F)

    # 対数振幅スペクトルを求める
    spectrum = 20 * np.log10(absF)

    # 周波数系列
    # サンプリング定理より、fftSize2 (ナイキスト周波数)より小さい周波数成分が有効
    freq = [i * sampling_rate / fftSize for i in range(fftSize2)]

    plt.plot(freq, spectrum[:fftSize2], linewidth=1.0, color='darkorange')
    plt.title('Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.xlim([0, 1000])
    plt.show()

if __name__ == '__main__':
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    print('sampling_rate: ', sampling_rate)

    left = int(float(sys.argv[2]) * sampling_rate)
    right = int(float(sys.argv[3]) * sampling_rate)

    waveform = waveform / 32768.0

    plot_spectrum(waveform[left:right], sampling_rate)
