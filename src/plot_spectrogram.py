#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import numpy as np
import scipy
import scipy.io.wavfile
import matplotlib.pyplot as plt
import pylab
import os

rootdir = os.path.dirname(os.getcwd())


def plot_spectrogram(waveform, sampling_rate):
    window_duration = 40.0 * 1.0e-3  # 窓関数の長さ(単位は秒)
    window_shift = 5.0 * 1.0e-3  # 窓関数をスライドさせる長さ(単位は秒)
    window_size = int(window_duration * sampling_rate)  # 窓関数のサンプル数
    # 隣接する窓関数の重なり
    window_overlap = int((window_duration - window_shift) * sampling_rate)
    window = scipy.hanning(window_size)  # 窓関数本体
    # TODO: vmin, vmax を適切に調整する
    sp, freqs, times, ax = plt.specgram(
        waveform,
        NFFT=window_size,
        Fs=sampling_rate,
        window=window,
        noverlap=window_overlap,
        cmap='hot',
        vmin=None,
        vmax=None
    )
    plt.title('Spectrogram')
    plt.xlabel('Time [sec]')
    plt.ylabel('Frequency [Hz]')
    plt.xlim([0, times[-1]])
    plt.ylim([0, freqs[-1]])
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('no input files')
        sys.exit(1)

    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    # 各標本の値を-1から1の範囲に変換
    waveform = waveform / 32768.0
    plot_spectrogram(waveform, sampling_rate)
