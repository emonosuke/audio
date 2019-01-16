import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import queue
from helpers import get_frequency
import time

samplerate = 16000
window = 0.2
channels = 1

FRAME_SIZE = int(samplerate * 0.1)  # 1600
N_FRAMES = 10
MAX_FREQ = 250

def audio_callback(indata, outdata, frames, time, status):
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

        if len(data) >= FRAME_SIZE:
            framedata = data[:FRAME_SIZE].flatten()
        else:
            framedata[:shift] = data.flatten()
            framedata = np.roll(framedata, -shift, axis=0)

    # framedata に対して基本周波数を推定する
    freq = min(get_frequency(framedata, samplerate), MAX_FREQ)

    # print(freq)

    plotdata[0] = freq
    plotdata = np.roll(plotdata, -1, axis=0)

    lines[0].set_ydata(plotdata)

    # print('Elapsed: ', time.time() - start)
    
    return lines


if __name__ == '__main__':
    q = queue.Queue()

    length = int(window * samplerate)

    framedata = np.zeros(FRAME_SIZE)
    plotdata = np.zeros(N_FRAMES)

    fig, ax = plt.subplots()

    # TODO: 補助線入れたい
    lines = ax.plot(plotdata)
    ax.axis((0, N_FRAMES, 0, 8000))
    ax.set_ylim([0, MAX_FREQ])

    stream = sd.Stream(channels=channels, samplerate=samplerate, callback=audio_callback)
    ani = FuncAnimation(fig, update_plot, interval=100, blit=True)
    with stream:
        plt.show()
