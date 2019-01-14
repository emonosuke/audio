"""Play an audio file using a limited amount of memory.

The soundfile module (http://PySoundFile.rtfd.io/) must be installed for
this to work.  NumPy is not needed.

In contrast to play_file.py, which loads the whole file into memory
before starting playback, this example program only holds a given number
of audio blocks in memory and is therefore able to play files that are
larger than the available RAM.

"""
import queue
import sys
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

BLOCKSIZE = 2048
BUFFERSIZE = 20

q = queue.Queue(maxsize=BUFFERSIZE)

event = threading.Event()


def callback(outdata, frames, time, status):
    assert frames == BLOCKSIZE
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort

    global plotdata
    # print(data.shape)
    plotdata = np.fromstring(data, dtype=np.short) * (2.0 ** 15)

    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data


def update_plot(frame):
    global plotdata

    # lines[0].set_ydata(plotdata[:, 0])
    
    return lines


if __name__ == '__main__':
    filename = sys.argv[1]

    length = 4096  # グラフに表示するサンプル数
    plotdata = np.zeros((length, 1))

    fig, ax = plt.subplots()
    lines = ax.plot(plotdata)  # グラフのリアルタイム更新の最初はプロットから
    ax.axis((0, len(plotdata), -1, 1))

    ani = FuncAnimation(fig, update_plot, interval=10, blit=True)

    with sf.SoundFile(filename) as f:
        for _ in range(BUFFERSIZE):
            data = f.buffer_read(BLOCKSIZE, dtype='float32')
            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue

        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=BLOCKSIZE,
            device=None, channels=f.channels, dtype='float32',
            callback=callback, finished_callback=event.set)
        with stream:
            plt.show()
            timeout = BLOCKSIZE * BUFFERSIZE / f.samplerate
            while data:
                data = f.buffer_read(BLOCKSIZE, dtype='float32')
                q.put(data, timeout=timeout)
            event.wait()  # Wait until playback is finished
