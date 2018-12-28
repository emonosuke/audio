"""
10秒程度の楽曲のメロディの音高を sub-harmonic summation(SHS) によって推定する
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import math

rootdir = os.path.dirname(os.getcwd())

DURATION = 0.2  # s
SHIFT = 0.1  # s

# ド=C, レ=D, ミ=E, ファ=F, ソ=G, ラ=A, シ=B

# F2(=41), ..., E3(=52)
BASE_FREQ = [65.406, 69.296, 73.416, 77.782, 82.407, 87.307, 92.499, 97.999, 103.83, 110.00, 116.54, 123.47]
NUM_CLASS = 12
NODE_NUM_BASE = 41
DECAY_RATE = 0.8


def calc_overtones(maxfreq):
    """
    基本周波数の候補の倍音を調べる

    Parameters
    ----------
    maxfreq: float
        ナイキスト周波数
    
    Returns
    ----------
    cands: array
        shape=(, tuple(3)) 
        (調べるべき周波数, 対応する基本周波数, 何倍音か)
    """
    cands = []

    for i in range(NUM_CLASS):
        # 倍音
        rep = 1
        b = BASE_FREQ[i]

        while(b * rep < maxfreq):
            cands.append((b * rep, i, rep))

            rep += 1
    
    cands = sorted(cands)

    # print(cands)

    return cands


def power_by_frequency(w, sr, cands):
    """
    F2(41) ~ E3(52) を基本周波数の候補とする

    Parameters
    ----------
    w: array
        波形
    sr: int
        サンプリング周波数
    cands: array
        shape=(tuple, 3)
    
    Returns
    ----------
    res: array
        shape=(12,) 
        node number = 41 ~ 52 に対応するパワー総和
    """
    res = np.zeros(NUM_CLASS)

    fftSize = 1 << math.ceil(math.log2(len(w)))
    fftSize2 = (fftSize >> 1) + 1

    w = [w[i] if i < len(w) else 0 for i in range(fftSize)]

    # 高速フーリエ変換
    F = np.fft.fft(w)
    spectrum = np.abs(F)

    # サンプリング定理より、fftSize2 (ナイキスト周波数)より小さい周波数成分が有効
    spectrum = spectrum[:fftSize2]
    freqs = [i * sampling_rate / fftSize for i in range(fftSize2)]

    cands_id = 0
    i = 0

    while(i < len(cands)):
        target_freq = cands[cands_id][0]
        target_node = cands[cands_id][1]
        target_rep = cands[cands_id][2]

        # target_freq にあたる周波数と最も近い freqs のスペクトルを得る
        while(freqs[i] < target_freq):
            i += 1
        
        if target_freq - freqs[i-1] <= freqs[i] - target_freq:
            power = spectrum[i-1]
            # picked_freqs.append(freqs[i-1])
        else:
            power = spectrum[i]
            # picked_freqs.append(freqs[i])
        
        res[target_node] += power * (DECAY_RATE ** (target_rep - 1)) 

        cands_id += 1

    # print(res)

    return res


def shs(w, sr):
    """
    フレームに分割して、各フレームに対して基本周波数の候補の倍音成分のパワーの総和を求める
    これが最大となる基本周波数の候補をメロディとする

    Parameters
    ----------
    w: array
        波形
    sr: int
        サンプリング周波数
    """
    # 基本周波数の候補の倍音を調べる
    cands = calc_overtones(sr / 2)

    left = 0
    right = DURATION * sr

    # 各フレームごと
    while right < len(waveform):
        print('===== {:.1f}s - {:.1f}s ====='.format(left / sr, right / sr))

        framed_w = waveform[int(left):int(right)]

        # 窓関数
        hanningwindow = np.hanning(len(framed_w))
        framed_w = hanningwindow * framed_w

        powers = power_by_frequency(framed_w, sr, cands)

        melody = np.argmax(powers)

        print('melody: Node number={:d} (Frequency={:.2f})'.format(melody + NODE_NUM_BASE, BASE_FREQ[melody]))

        left += SHIFT * sr
        right += SHIFT * sr


if __name__ == '__main__':
    # wavfile 読み込み
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    shs(waveform, sampling_rate)
