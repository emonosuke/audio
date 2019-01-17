import sys
import math
import numpy as np
import time
import sounddevice as sd
import soundfile as sf
import subprocess
from multiprocessing import Process

PLAYER_FRAME_DURATION = 0.1
PLAYER_FRAME_SHIFT = 0.05
PLAYER_N_PLOTS = 20


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
        self.filename = filename
        self.waveform = waveform
        self.samplerate = samplerate
        self.specgrams = calc_specgrams(waveform, samplerate)
        
        # For colormap
        self.specmax = np.max(self.specgrams)
        self.specmin = np.min(self.specgrams)

        self.lenfreq = ((int(self.samplerate * PLAYER_FRAME_DURATION) >> 1) + 1)
        self.plotdata = np.zeros((PLAYER_N_PLOTS, self.lenfreq))
        self.readed = 0

    def play(self):
        self.started = time.time()

        def playback(filename):
            subprocess.call(['play', '-q', filename])

        proc = Process(target=playback, args=(self.filename,))
        proc.start()

        # その後、一定時間ごとに plotdata 更新

    
    def update(self):
        if self.readed >= len(self.specgrams):
            return self.plotdata
        
        elapsed = time.time() - self.started
        # print("elapsed: ", elapsed)
        if elapsed >= (self.readed + 1) * PLAYER_FRAME_SHIFT:
            self.readed += 1
            self.plotdata[0] = self.specgrams[self.readed]
            self.plotdata = np.roll(self.plotdata, -1, axis=0)

        return self.plotdata


if __name__ == '__main__':
    filename = sys.argv[1]
    p = Player(filename)
    p.play()
    print(p.specgrams)
    # playback
    time.sleep(5)
