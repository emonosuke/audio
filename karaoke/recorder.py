from threading import Thread
import queue
import sys
import numpy as np
import sounddevice as sd
import time

SAMPLERATE = 16000
PLOT_LEN = int(SAMPLERATE * 0.2)
N_CHANNELS = 1


class Recorder(Thread):
    def __init__(self):
        super(Recorder, self).__init__()
        self.waveform = np.zeros((PLOT_LEN, 1))
        self.q = queue.Queue()
    
    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        outdata[:] = indata
        self.q.put(indata)

    def run(self):
        stream = sd.Stream(channels=N_CHANNELS, samplerate=SAMPLERATE, callback=self.callback)
        stream.start()

if __name__ == '__main__':
    th = Recorder()
    th.start()
    while 1:
        time.sleep(1)
        data = th.q.get_nowait()
        print(data)
