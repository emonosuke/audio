import queue
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import queue


def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)

    global q

    q.put(indata)


def update_plot(frame):
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

        shift = len(data)

        print(shift)

        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data

        # TODO: plotdata に対して基本周波数を推定する

        lines[0].set_ydata(plotdata[:, 0])
    
    return lines


if __name__ == '__main__':
    samplerate = 16000
    window = 0.2
    interval = 100
    channels = 1

    q = queue.Queue()

    length = int(window * samplerate)   # グラフに表示するサンプル数
    plotdata = np.zeros((length, 1))

    fig, ax = plt.subplots()
    lines = ax.plot(plotdata)          # グラフのリアルタイム更新の最初はプロットから
    ax.axis((0, len(plotdata), -1, 1))

    stream = sd.InputStream(channels=channels, samplerate=samplerate, callback=audio_callback)
    ani = FuncAnimation(fig, update_plot, interval=interval, blit=True)
    with stream:
        plt.show()
