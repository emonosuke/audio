"""
10秒程度の楽曲から spectrogram と chromagram を表示
chroma vector を計算して、和音の認識をする
"""

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
import os
import math

rootdir = os.path.dirname(os.getcwd())

DURATION = 0.4  # s
SHIFT = 0.2  # s

# ド=C, レ=D, ミ=E, ファ=F, ソ=G, ラ=A, シ=B

# C1, C#1, D1, D#1, E1, F1, F#1, G1, G#1, A1, A#1, B1
BASE_FREQ = [32.703, 34.648, 36.708, 38.891, 41.203, 43.654, 46.249, 48.999, 51.913, 55.000, 58.270, 61.735]
NUM_CLASS = 12
NUM_OCTAVE = 7

CHORD_DICT = {
    0: 'C Major',
    1: 'C# Major',
    2: 'D Major',
    3: 'D# Major',
    4: 'E Major',
    5: 'F Major',
    6: 'F# Major',
    7: 'G Major',
    8: 'G# Major',
    9: 'A Major',
    10: 'A# Major',
    11: 'B Major',
    12: 'C Minor',
    13: 'C# Minor',
    14: 'D Minor',
    15: 'D# Minor',
    16: 'E Minor',
    17: 'F Minor',
    18: 'F# Minor',
    19: 'G Minor',
    20: 'G# Minor',
    21: 'A Minor',
    22: 'A# Minor',
    23: 'B Minor',
}


def chroma_vector(w, sr):
    """
    C1 ~ B7 (0 ~ 83)の範囲について、ピッチクラスごとの振幅スペクトルの和を計算する

    Parameters
    ----------
    w: array
        波形
    sr: int
        サンプリング周波数
    
    Returns
    ----------
    cvs: array
        shape=(12,) 
        chroma vector
    """
    fftSize = 1 << math.ceil(math.log2(len(w)))
    fftSize2 = (fftSize >> 1) + 1

    w = [w[i] if i < len(w) else 0 for i in range(fftSize)]

    # 高速フーリエ変換
    F = np.fft.fft(w)
    spectrum = np.abs(F)

    # サンプリング定理より、fftSize2 (ナイキスト周波数)より小さい周波数成分が有効
    spectrum = spectrum[:fftSize2]
    freqs = [i * sampling_rate / fftSize for i in range(fftSize2)]

    # ピッチクラスごとのスペクトル和
    cvs = np.zeros(NUM_CLASS)
    picked_freqs = []

    target_id = 0
    i = 0

    while(target_id < NUM_CLASS * NUM_OCTAVE):
        class_id = target_id % NUM_CLASS
        octave_id = target_id // NUM_CLASS

        target_freq = BASE_FREQ[class_id] * (2 ** (octave_id))

        # target_freq にあたる周波数と最も近い freqs のスペクトルを得る
        while(freqs[i] < target_freq):
            i += 1
        
        if target_freq - freqs[i-1] <= freqs[i] - target_freq:
            power = spectrum[i-1]
            # picked_freqs.append(freqs[i-1])
        else:
            power = spectrum[i]
            # picked_freqs.append(freqs[i])
        
        cvs[class_id] += power 

        target_id += 1
    
    # print("chroma vectors: ", cvs)
    # print(picked_freqs)

    return cvs


def likely_chord(cvs):
    """
    C Major(=0), C# Major(=1), ..., B Minor(=23) の和音らしさを計算して、
    最大のものを出力する
    和音 c の和音らしさ L(c) = 1.0 * CV(c_root) + 0.5 * CV(c_3rd) + 0.8 * CV(c_5th)
    """
    L = []

    # For Major chord
    first, third, fifth = 0, 4, 7

    while(first < NUM_CLASS):
        lc = 1.0 * cvs[first] + 0.5 * cvs[third] + 0.8 * cvs[fifth]
        L.append(lc)

        first += 1
        third = (third + 1) % NUM_CLASS
        fifth = (fifth + 1) % NUM_CLASS
    
    # For Minor chord
    first, third, fifth = 0, 3, 7

    while(first < NUM_CLASS):
        lc = 1.0 * cvs[first] + 0.5 * cvs[third] + 0.8 * cvs[fifth]
        L.append(lc)

        first += 1
        third = (third + 1) % NUM_CLASS
        fifth = (fifth + 1) % NUM_CLASS
  
    # print(L)
    return np.argmax(L)


def predict_chord(w, sr):
    """
    フレームに分割して、各フレームに対して chroma vector を計算したのち和音の尤度が最大となる
    和音を推定結果とする
    各フレームに対して、その時間と和音の推定結果を標準出力する

    Parameters
    ----------
    w: array
        波形
    sr: int
        サンプリング周波数
    """
    left = 0
    right = DURATION * sampling_rate

    # 各フレームごと
    while right < len(waveform):
        framed_w = waveform[int(left):int(right)]

        # 窓関数
        hanningwindow = np.hanning(len(framed_w))
        framed_w = hanningwindow * framed_w

        cvs = chroma_vector(framed_w, sampling_rate)
        
        r = likely_chord(cvs)

        print('===== {:.1f}s - {:.1f}s ====='.format(left / sampling_rate, right / sampling_rate))
        print('chord recognition: ', CHORD_DICT[r])

        left += SHIFT * sampling_rate
        right += SHIFT * sampling_rate


if __name__ == '__main__':
    # wavfile 読み込み
    datadir = os.path.join(rootdir, 'data')
    filename = os.path.join(datadir, sys.argv[1])
    sampling_rate, waveform = scipy.io.wavfile.read(filename)

    predict_chord(waveform, sampling_rate)
