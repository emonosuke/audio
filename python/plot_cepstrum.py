#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
./plot_spectrum.py wavfile left[sec] right[sec]
left[sec] と right[sec] 間の cpestrum を表示
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import math

rootdir = os.path.dirname(os.getcwd())


def get_spectrum(waveform, sampling_rate):
    lenw = len(waveform)

    # fftSize = 2^p >= lenw を満たす fftSize を求める
    fftSize = 1 << math.ceil(math.log2(lenw))
    fftSize2 = fftSize >> 1

    # 信号長を fftSize に伸ばし、足りない部分は0で埋める
    w = [waveform[i] if i < lenw else 0 for i in range(fftSize)]

    # 高速フーリエ変換
    F = np.fft.fft(w)
    absF = np.abs(F)

    # 対数振幅スペクトルを求める
    spectrum = 20 * np.log10(absF)

    # サンプリング定理より、fftSize2 (ナイキスト周波数)より小さい周波数成分が有効
    freq = [i * sampling_rate / fftSize for i in range(fftSize2)]

    return freq, spectrum[:fftSize2]


def plot_cepstrum(waveform, sampling_rate):
    freq, spectrum = get_spectrum(waveform, sampling_rate)

    lens = len(spectrum)
    print('spectrum length: ', lens)

    F = np.fft.fft(spectrum)

    # print(F[:13].real)
    # print(F[(lens - 13):].real)
    # 1 から 13 次までの cepstrum 係数を抽出する
    cepF = [F[i] if i < 13 or i > lens - 13 else 0 for i in range(lens)]

    f = np.fft.ifft(cepF)
    cepstrum = f.real

    print('cepstrum length: ', len(cepstrum))

    plt.plot(freq, spectrum, linewidth=1.0, color='darkorange')
    plt.plot(freq, cepstrum, linewidth=2.0, color='red')
    plt.title('Cepstrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.xlim([0, 1000])
    plt.show()


if __name__ == '__main__':
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    print('length of waveform: ', len(waveform))
    print('sampling_rate: ', sampling_rate)

    left_t = 0
    right_t = len(waveform)

    # left, right が与えられてなければファイル全体とする
    if len(sys.argv) >= 3:
        left_t = float(sys.argv[2])
    if len(sys.argv) >= 4:
        right_t = float(sys.argv[3])

    left = int(left_t * sampling_rate)
    right = int(right_t * sampling_rate)

    waveform = waveform / 32768.0

    plot_cepstrum(waveform[left:right], sampling_rate)
