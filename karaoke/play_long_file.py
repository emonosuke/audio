"""Play an audio file using a limited amount of memory.

The soundfile module (http://PySoundFile.rtfd.io/) must be installed for
this to work.  NumPy is not needed.

In contrast to play_file.py, which loads the whole file into memory
before starting playback, this example program only holds a given number
of audio blocks in memory and is therefore able to play files that are
larger than the available RAM.

"""
from __future__ import division, print_function
import argparse
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.x
import sys
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename', help='audio file to be played back')
parser.add_argument('-d', '--device', type=int_or_str,
                    help='output device (numeric ID or substring)')
parser.add_argument('-b', '--blocksize', type=int, default=2048*5,
                    help='block size (default: %(default)s)')
parser.add_argument(
    '-q', '--buffersize', type=int, default=20*5,
    help='number of blocks used for buffering (default: %(default)s)')
args = parser.parse_args()
if args.blocksize == 0:
    parser.error('blocksize must not be zero')
if args.buffersize < 1:
    parser.error('buffersize must be at least 1')

q = queue.Queue(maxsize=args.buffersize)
event = threading.Event()


def callback(outdata, frames, time, status):
    assert frames == args.blocksize
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    data = q.get_nowait()
    
    global plotdata
    plotdata = np.frombuffer(data, dtype=np.int16)
    plotdata = plotdata / (2.0 ** 15)
    print(plotdata.shape)
    # print(plotdata[:100])

    if len(data) < len(outdata):
        # called last
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data

def update_plot(frame):
    """
    matplotlibのアニメーション更新毎に呼ばれるグラフ更新関数
    """
    global plotdata
    
    lines[0].set_ydata(plotdata[-1000:])
    
    return lines


filename = sys.argv[1]

length = 1000  # グラフに表示するサンプル数
plotdata = np.zeros((length, 1))

fig, ax = plt.subplots()
lines = ax.plot(plotdata, linewidth=0.5, color='darkorange')  # グラフのリアルタイム更新の最初はプロットから
ax.axis((0, len(plotdata), -1, 1))

ani = FuncAnimation(fig, update_plot, interval=100, blit=True)

try:
    import sounddevice as sd
    import soundfile as sf

    with sf.SoundFile(args.filename) as f:
        for _ in range(args.buffersize):
            data = f.buffer_read(args.blocksize, dtype='float32')
            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue

        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=args.blocksize,
            channels=f.channels, dtype='float32',
            callback=callback, finished_callback=event.set)
        with stream:
            plt.show()
            timeout = args.blocksize * args.buffersize / f.samplerate
            while data:
                data = f.buffer_read(args.blocksize, dtype='float32')
                q.put(data, timeout=timeout)
            # called last
            event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except queue.Full:
    # A timeout occured, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
