import sys
import math
import numpy as np
import time
import sounddevice as sd
import soundfile as sf
import subprocess
from multiprocessing import Process
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

PLAYER_FRAME_DURATION = 0.2
PLAYER_FRAME_SHIFT = 0.1
PLAYER_N_PLOTS = 20
PLAYER_UPDATE_INTERVAL = 0.05

PLAYER_SAMPLERATE = 16000  # samplerate is fixed value
PLAYER_NYQUIST = PLAYER_SAMPLERATE // 2

PLAYER_LIM_FREQ = 1000
PLAYER_LENFREQ = ((int(PLAYER_SAMPLERATE * PLAYER_FRAME_DURATION) >> 1) + 1) // (PLAYER_NYQUIST // PLAYER_LIM_FREQ)


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
    def __init__(self, filename, q):
        super(Player, self).__init__()
        
        waveform, samplerate = sf.read(sys.argv[1], dtype='float32')

        if samplerate != PLAYER_SAMPLERATE:
            print("ERROR in player: input wav file's sampling rate must be equal to 16,000")
            sys.exit(1)
        
        self.waveform = waveform

        self.filename = filename
        self.specgrams = calc_specgrams(waveform, samplerate)
        
        # For colormap
        # specmax = np.max(self.specgrams)
        # specmin = np.min(self.specgrams)

        # print(specmin, specmax)

        self.readed = 0

        q.put(0)

    def play(self, q):
        self.specgrams = calc_specgrams(self.waveform, PLAYER_SAMPLERATE)
        
        # playback start
        self.started = time.time()

        def playback(filename):
            # TODO: do not use dependency(sox)
            subprocess.call(['play', '-q', filename])

        pb = Process(target=playback, args=(self.filename,))
        pb.start()
        
        while 1:
            time.sleep(PLAYER_UPDATE_INTERVAL)

            # update freq
            elapsed = time.time() - self.started

            if elapsed >= (self.readed + 1) * PLAYER_FRAME_SHIFT:
                self.readed += 1

                if self.readed >= len(self.specgrams):
                    break
                
                # put latest specgram to queue
                q.put(self.specgrams[self.readed][:PLAYER_LENFREQ])
                # q.put(elapsed)
                # q.put(self.readed)


def player_main(filename, q):
    p = Player(filename, q)
    p.play(q)
