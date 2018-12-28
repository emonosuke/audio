#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
librosa によって chromagram を表示する
"""

import librosa
import librosa.display
import os
import matplotlib.pyplot as plt
import sys

# wavfile の PATH は data/ を基準とする
rootdir = os.path.dirname(os.getcwd())
datadir = os.path.join(rootdir, 'data')

filename = os.path.join(datadir, sys.argv[1])
y, sr = librosa.load(filename)

C = librosa.feature.chroma_cens(y=y, sr=sr)

librosa.display.specshow(
    C,
    sr=sr,
    x_axis='time',
    y_axis='chroma',
    cmap='hot',
    vmin=0,
    vmax=1
)

plt.title('Chromagram')
plt.colorbar()
plt.show()
