import math
import wave
import numpy as np
import time
import matplotlib.pyplot as plt
from optparse import OptionParser
from threading import Thread

from player import Player
from recorder import Recorder

DELTA_TIME = 0.001  # seconds
PLOT_FRAMES = 50
PLOT_FREQ_MAX = 2000.0


class plotter(object):
    def __init__(self,
                 player,
                 recorder,
                 plot_frames=PLOT_FRAMES,
                 plot_freq_max=PLOT_FREQ_MAX,
                 delta_time=DELTA_TIME):
        self.p = player
        self.r = recorder
        self.plot_frames = plot_frames
        self.plot_freq_max = plot_freq_max
        self.delta_time = delta_time

        self.current_frame = -1
        self.p_rms = np.zeros(self.plot_frames)
        self.r_rms = np.zeros(self.plot_frames)
        self.p_spectrogram = np.ndarray([self.plot_frames, self.p.frame_size // 2 + 1])
        self.p_spectrogram.fill(20.0 * math.log(1.0e-1))
        self.r_spectrogram = np.ndarray([self.plot_frames, self.r.frame_size // 2 + 1])
        self.r_spectrogram.fill(20.0 * math.log(1.0e-1))
        self.p_nyquist = self.p.sampling_rate * 0.5
        self.r_nyquist = self.r.sampling_rate * 0.5
        self.p_freqs = np.linspace(0.0, self.p_nyquist, self.p.frame_size // 2 + 1)
        self.r_freqs = np.linspace(0.0, self.r_nyquist, self.r.frame_size // 2 + 1)

        self.p_plot_freq_max_index = next(
            x[1] for x in zip(self.p_freqs, range(len(self.p_freqs)))
            if x[0] > self.plot_freq_max
        )
        self.r_plot_freq_max_index = next(
            x[1] for x in zip(self.r_freqs, range(len(self.r_freqs)))
            if x[0] > self.plot_freq_max
        )

        self.updated = True

    def __call__(self):
        plt.ion()  # interactive mode on
        loop = plotterloop(self)
        loop.start()

        while True:
            if not self.updated:
                time.sleep(self.delta_time)
                continue
            plt.clf()  # clear plot
            self.plot_player_rms()
            self.show_player_spec()
            self.plot_recorder_rms()
            self.show_recorder_spec()
            plt.draw()
            self.updated = False

    def plot_player_rms(self):
        plt.subplot(221)
        times = (np.arange(self.plot_frames) - self.plot_frames + self.current_frame + 1) / self.p.frame_rate
        plt.plot(times, self.p_rms, 'o-b')

    def show_player_spec(self):
        plt.subplot(222)
        extent = [(self.current_frame - self.plot_frames) / self.p.frame_rate,
                  self.current_frame / self.p.frame_rate,
                  0.0, self.plot_freq_max]
        plt.imshow(np.transpose(self.p_spectrogram[:, : self.p_plot_freq_max_index]),
                   extent=extent, origin='lower', aspect='auto')
    
    def plot_recorder_rms(self):
        plt.subplot(223)
        times = (np.arange(self.plot_frames) - self.plot_frames + self.current_frame + 1) / self.r.frame_rate
        plt.plot(times, self.r_rms, 'o-b')
    
    def show_recorder_spec(self):
        plt.subplot(224)
        extent = [(self.current_frame - self.plot_frames) / self.r.frame_rate,
                  self.current_frame / self.r.frame_rate,
                  0.0, self.plot_freq_max]
        plt.imshow(np.transpose(self.r_spectrogram[:, : self.r_plot_freq_max_index]),
                   extent=extent, origin='lower', aspect='auto')
    
    def update(self):
        if not self.p.queue.empty():
            wframe = self.p.queue.get()
            self.p_rms[0] = self.rms(wframe)
            self.p_rms = np.roll(self.p_rms, -1)
            self.p_spectrogram[0] = np.log(np.abs(np.fft.rfft(wframe)))
            self.p_spectrogram = np.roll(self.p_spectrogram, -1, axis=0)
        
        if not self.r.queue.empty():
            wframe = self.r.queue.get()
            self.r_rms[0] = self.rms(wframe)
            self.r_rms = np.roll(self.r_rms, -1)
            self.r_spectrogram[0] = np.log(np.abs(np.fft.rfft(wframe)))
            self.r_spectrogram = np.roll(self.r_spectrogram, -1, axis=0)
        
        self.updated = True
    
    def rms(self, a):
        return math.sqrt(np.dot(a, a) / len(a))


class plotterloop(Thread):
    def __init__(self, plotter):
        super(plotterloop, self).__init__()
        self.setDaemon(True)
        self.plotter = plotter
    
    def run(self):
        while True:
            if self.plotter.p.queue.empty() and self.plotter.r.queue.empty():
                time.sleep(DELTA_TIME * 100)
                continue
            self.plotter.update()


def main():
    parser = OptionParser()
    parser.add_option('-v',
                      '--verbose',
                      dest='verbose',
                      action='store_true',
                      default=False,
                      help='verbose output')
    (options, args) = parser.parse_args()
    verbose = options.verbose

    if len(args) == 0:
        print('no input files.')
        sys.exit()
    
    filename = args[0]
    p = Player(filename)

    """
    r = Recorder()
    r.start()
    """

    pl = plotter(p, r)
    th = Thread(target=pl)
    th.daemon = True
    th.start()

    p.run()

if __name__ == '__main__':
    main()
