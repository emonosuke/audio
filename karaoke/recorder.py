from threading import Thread
from multiprocessing import Process
import queue
import sys
import numpy as np
import sounddevice as sd
import time
from helpers import get_frequency

RECORDER_SAMPLERATE = 16000
RECORDER_N_CHANNELS = 1

RECORDER_FRAME_DURATION = 0.1
RECORDER_FRAME_SIZE = int(RECORDER_SAMPLERATE * RECORDER_FRAME_DURATION)
RECORDER_N_FRAMES = 20

RECORDER_MAX_FREQ = 500


class Recorder(Process):
    def __init__(self):
        super(Recorder, self).__init__()
        self.q = queue.Queue()

        self.framedata = np.zeros(RECORDER_FRAME_SIZE)
        self.plotdata = np.zeros(RECORDER_N_FRAMES)
    
    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        outdata[:] = indata
        self.q.put(indata)

    def run(self):
        stream = sd.InputStream(device=2, channels=RECORDER_N_CHANNELS, samplerate=RECORDER_SAMPLERATE, callback=self.callback)
        stream.start()
    
    def update(self):
        while True:
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                break

            shift = len(data)

            self.framedata[:shift] = data.flatten()
            self.framedata = np.roll(self.framedata, -shift, axis=0)

        # framedata に対して基本周波数を推定する
        freq = min(get_frequency(self.framedata, RECORDER_SAMPLERATE), RECORDER_MAX_FREQ)

        print(freq)

        self.plotdata[0] = freq
        self.plotdata = np.roll(self.plotdata, -1, axis=0)

if __name__ == '__main__':
    th = Recorder()

    th.start()

    while 1:
        time.sleep(1)
        th.update()
