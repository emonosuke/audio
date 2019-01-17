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
import multiprocessing
from player import player_main


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
            framedata = data[-RECORDER_FRAME_SIZE:].flatten()
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


def update_player_plot(frame):
    while 1:
        try:
            top = player_queue.get_nowait()
        except:
            # expect empty queue
            break
    
    print("player caller: ", top)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='wav file to play')

    args = parser.parse_args()

    # Recorder
    q = queue.Queue()

    framedata = np.zeros(RECORDER_FRAME_SIZE)
    plotdata = np.zeros(RECORDER_N_FRAMES)

    fig1, ax1 = plt.subplots()

    # fig2, ax2 = plt.subplots()
    
    # TODO: 補助線入れたい
    lines = ax1.plot(plotdata)
    ax1.axis((0, RECORDER_N_FRAMES, 0, RECORDER_MAX_FREQ / 2))

    stream = sd.Stream(channels=RECORDER_N_CHANNELS, samplerate=RECORDER_SAMPLERATE, callback=callback)
    ani1 = FuncAnimation(fig1, update_plot, interval=100, blit=True)
    # ani2 = FuncAnimation(fig2, update_player_plot, interval=100, blit=True)

    player_queue = multiprocessing.Queue()

    p = multiprocessing.Process(target=player_main, args=(args.filename, player_queue))

    p.start()

    with stream:
        plt.show()
