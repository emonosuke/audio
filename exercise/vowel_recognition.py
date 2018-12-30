#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
a.wav, i.wav, u.wav, e.wav, o.wav を訓練データとして、
識別器を構成してテストデータである wavfile の認識結果を表示する
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import math

# wavfile の PATH は data/ を基準とする
rootdir = os.path.dirname(os.getcwd())
datadir = os.path.join(rootdir, 'data')

PATH_A = os.path.join(datadir, 'a.wav')
PATH_I = os.path.join(datadir, 'i.wav')
PATH_U = os.path.join(datadir, 'u.wav')
PATH_E = os.path.join(datadir, 'e.wav')
PATH_O = os.path.join(datadir, 'o.wav')

frameDuration = 0.2  # s
frameShift = 0.1  # s

alps = {0: 'a', 1: 'i', 2: 'u', 3: 'e', 4: 'o'}


def get_spectrum(sr, w):
    lenw = len(w)

    # fftSize = 2^p >= lenw を満たす fftSize を求める
    fftSize = 1 << math.ceil(math.log2(lenw))
    fftSize2 = fftSize >> 1

    # 信号長を fftSize に伸ばし、足りない部分は0で埋める
    w = [w[i] if i < lenw else 0 for i in range(fftSize)]

    # 高速フーリエ変換
    F = np.fft.fft(w)
    absF = np.abs(F)

    # 対数振幅スペクトルを求める
    spectrum = 20 * np.log10(absF)

    return spectrum[:fftSize2]


def get_cepstrum(sr, w):
    # 窓関数
    hanningwindow = np.hanning(len(w))
    w = hanningwindow * w

    spectrum = get_spectrum(sr, w)

    F = np.fft.fft(spectrum)

    return F[:13].real


def train():
    """
    モデル L_0(a), L_1(i), L_2(u), L_3(e), L_4(o) の mean, var を学習する
    """
    sampling_rate, aw = scipy.io.wavfile.read(PATH_A)
    _, iw = scipy.io.wavfile.read(PATH_I)
    _, uw = scipy.io.wavfile.read(PATH_U)
    _, ew = scipy.io.wavfile.read(PATH_E)
    _, ow = scipy.io.wavfile.read(PATH_O)

    aw = aw / 32768.0
    iw = iw / 32768.0
    uw = uw / 32768.0
    ew = ew / 32768.0
    ow = ow / 32768.0

    # a, i, u, e, o に対応するケプストラム
    cep_a = []
    cep_i = []
    cep_u = []
    cep_e = []
    cep_o = []

    left = 0
    right = frameDuration * sampling_rate

    while right < len(aw):
        cep_a.append(get_cepstrum(sampling_rate, aw[int(left):int(right)]))
        cep_i.append(get_cepstrum(sampling_rate, iw[int(left):int(right)]))
        cep_u.append(get_cepstrum(sampling_rate, uw[int(left):int(right)]))
        cep_e.append(get_cepstrum(sampling_rate, ew[int(left):int(right)]))
        cep_o.append(get_cepstrum(sampling_rate, ow[int(left):int(right)]))

        left += frameShift * sampling_rate
        right += frameShift * sampling_rate
    
    mean_a = np.mean(cep_a, axis=0)
    mean_i = np.mean(cep_i, axis=0)
    mean_u = np.mean(cep_u, axis=0)
    mean_e = np.mean(cep_e, axis=0)
    mean_o = np.mean(cep_o, axis=0)
    
    std_a = np.std(cep_a, axis=0)
    std_i = np.std(cep_i, axis=0)
    std_u = np.std(cep_u, axis=0)
    std_e = np.std(cep_e, axis=0)
    std_o = np.std(cep_o, axis=0)

    return [mean_a, mean_i, mean_u, mean_e, mean_o], [std_a, std_i, std_u, std_e, std_o]


def calc_likelihood(x, mean, std):
    """
    対数尤度を求める
    - \sum_d (log(std_d) + (x_d - mean_d)^2 / (2 * std_d^2))
    """
    p = 0
    n = len(x)

    for i in range(n):
        p -= math.log(std[i]) + ((x[i] - mean[i]) ** 2) / (2 * (std[i] ** 2))

    return p


def predict(sr, w, means, stds):
    # 認識結果
    res = []

    left = 0
    right = frameDuration * sampling_rate

    while right < len(w):
        cep = get_cepstrum(sr, w[int(left):int(right)])

        # 'a' の対数尤度を求める
        maxl = calc_likelihood(cep, means[0], stds[0])
        argmaxl = 0
        for c in range(1, 5):
            l = calc_likelihood(cep, means[c], stds[c])
            if l > maxl:
                maxl = l
                argmaxl = c

        res.append(alps[argmaxl])

        left += frameShift * sampling_rate
        right += frameShift * sampling_rate
    
    return res


if __name__ == '__main__':
    filename = os.path.join(datadir, sys.argv[1])

    # train phase
    means, stds = train()

    # test phase
    sampling_rate, testw = scipy.io.wavfile.read(filename)
    testw = testw / 32768.0
    print(predict(sampling_rate, testw, means, stds))
