import sys
import math
import numpy as np
import time
import sounddevice as sd
import soundfile as sf
import subprocess
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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


class Player(Process):
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
    
    def update_plot(self):
        elapsed = time.time() - self.started
        if elapsed >= (self.readed + 1) * PLAYER_FRAME_SHIFT:
            self.readed += 1
            self.plotdata[0] = self.specgrams[self.readed]
            self.plotdata = np.roll(self.plotdata, -1, axis=0)

        self.im.set_array(np.transpose(self.plotdata))

        return self.im,

    def run(self):
        self.specgrams = calc_specgrams(self.waveform, self.samplerate)

        # initialize spectrogram
        fig, ax = plt.subplots()
        
        extent = [0.0, 1.0, 0.0, self.samplerate / 2]

        self.im = plt.imshow(np.transpose(self.plotdata), cmap='hot', origin='lower', aspect='auto', extent=extent)
        
        # playback start
        self.started = time.time()

        def playback(filename):
            subprocess.call(['play', '-q', filename])

        pb = Process(target=playback, args=(self.filename,))
        pb.start()

        # TODO: when to proc.join()

        ani = FuncAnimation(fig, self.update_plot, interval=100, blit=True)
    
        plt.show()
