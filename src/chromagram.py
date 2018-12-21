"""
librosa によって chromagram を表示する
"""

import librosa

# wavfile の PATH は data/ を基準とする
rootdir = os.path.dirname(os.getcwd())
datadir = os.path.join(rootdir, 'data')
