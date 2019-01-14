import sys
import math
import numpy as np
import scipy
import scipy.io.wavfile
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation

FRAME_DURATION = 0.2
FRAME_SHIFT = 0.1

def plot_spectrogram(waveform, sampling_rate):
    global arr

    arr = np.roll(arr, -1, axis=0)
    
    extent = [0.0, 0.4, 0.0, 8000]
    plt.imshow(np.transpose(arr), cmap='hot', origin='lower', aspect='auto', extent=extent)
    plt.show()

"""
def update_plot(frame):
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

        # TODO: plotdata に対して基本周波数を推定する

        lines[0].set_ydata(plotdata[:, 0])
    
    return lines
"""

def updatefig(*args):
    global arr

    arr = np.roll(arr, -1, axis=0)

    extent = [0.0, 0.4, 0.0, 8000]

    im.set_array(np.transpose(arr))
    # plt.imshow(np.transpose(arr), cmap='hot', origin='lower', aspect='auto', extent=extent)

    return im,


if __name__ == '__main__':
    fig, ax = plt.subplots()

    arr = [[1, 2, 3, 4, 5, 6],
             [2, 1, 2, 3, 4, 5],
             [3, 2, 1, 2, 3, 4]]
    
    extent = [0.0, 0.4, 0.0, 8000]

    im = plt.imshow(np.transpose(arr), cmap='hot', origin='lower', aspect='auto', extent=extent)

    ani = FuncAnimation(fig, updatefig, interval=10, blit=True)

    plt.show()

    # sampling_rate, waveform = scipy.io.wavfile.read(sys.argv[1])

    # 各標本の値を-1から1の範囲に変換
    # waveform = waveform / 32768.0
