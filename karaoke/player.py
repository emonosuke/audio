import sys
import math
import numpy as np
import time
import sounddevice as sd
import soundfile as sf

PLAYER_FRAME_DURATION = 0.2
PLAYER_FRAME_SHIFT = 0.1


def calc_specgrams(waveform, samplerate):
    specgrams = []

    left = 0
    right = PLAYER_FRAME_DURATION * samplerate

    while right < len(waveform):
        wframe = waveform[int(left):int(right)]

        hanningwindow = np.hanning(len(wframe))
        wframe = hanningwindow * wframe

        specgrams.append(np.log(np.abs(np.fft.rfft(wframe))))

        left += PLAYER_FRAME_SHIFT * samplerate
        right += PLAYER_FRAME_SHIFT * samplerate
    
    return specgrams


class Player():
    def __init__(self, filename):
        super(Player, self).__init__()
        
        waveform, samplerate = sf.read(sys.argv[1], dtype='float32')
        self.waveform = waveform
        self.samplerate = samplerate
        self.specgrams = calc_specgrams(waveform, samplerate)
        self.readed = 0

    def play(self):
        self.started = time.time()
        sd.play(self.waveform, self.samplerate)


if __name__ == '__main__':
    filename = sys.argv[1]
    p = Player(filename)
    p.play()
    print(p.specgrams)
    # playback
    time.sleep(5)
