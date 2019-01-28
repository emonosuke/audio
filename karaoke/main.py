import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import queue
from helpers import get_frequency
import time
from player import Player
import argparse
from threading import Thread

RECORDER_SAMPLERATE = 16000
RECORDER_N_CHANNELS = 1

RECORDER_FRAME_DURATION = 0.1
RECORDER_FRAME_SIZE = int(RECORDER_SAMPLERATE * RECORDER_FRAME_DURATION)
RECORDER_N_FRAMES = 20

RECORDER_MAX_FREQ = 500


def callback(indata, outdata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    outdata[:] = indata

    global q

    q.put(indata)


def update_plot(frame):
    start = time.time()

    global plotdata, framedata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

        shift = len(data)

        if len(data) >= RECORDER_FRAME_SIZE:
            framedata = data[-RECORDERFRAME_SIZE:].flatten()
        else:
            framedata[:shift] = data.flatten()
            framedata = np.roll(framedata, -shift, axis=0)

    # framedata に対して基本周波数を推定する
    freq = min(get_frequency(framedata, RECORDER_SAMPLERATE), RECORDER_MAX_FREQ)

    # print(freq)

    plotdata[0] = freq
    plotdata = np.roll(plotdata, -1, axis=0)

    lines[0].set_ydata(plotdata)

    # print('Elapsed: ', time.time() - start)
    
    return lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='wav file to play')

    args = parser.parse_args()

    # Recorder
    q = queue.Queue()

    framedata = np.zeros(RECORDER_FRAME_SIZE)
    plotdata = np.zeros(RECORDER_N_FRAMES)

    fig, ax = plt.subplots()

    # TODO: 補助線入れたい
    lines = ax.plot(plotdata)
    ax.axis((0, RECORDER_N_FRAMES, 0, RECORDER_MAX_FREQ / 2))

    stream = sd.Stream(channels=RECORDER_N_CHANNELS, samplerate=RECORDER_SAMPLERATE, callback=callback)
    ani = FuncAnimation(fig, update_plot, interval=100, blit=True)

    pl = Player(filename=args.filename)

    th = Thread(target=pl)
    th.daemon = True
    th.start()

    with stream:
        plt.show()
