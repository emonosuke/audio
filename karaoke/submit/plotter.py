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
from player import PLAYER_SAMPLERATE, PLAYER_LENFREQ, PLAYER_LIM_FREQ

RECORDER_SAMPLERATE = 16000
RECORDER_N_CHANNELS = 1

RECORDER_FRAME_DURATION = 0.1
RECORDER_FRAME_SIZE = int(RECORDER_SAMPLERATE * RECORDER_FRAME_DURATION)
RECORDER_N_FRAMES = 20

RECORDER_MAX_FREQ = 500

PLAYER_N_FRAMES = 100

RECORDER_PLOT_INTERVAL = 100 
PLAYER_PLOT_INTERVAL = 30

PLAYER_VMIN = -7.0
PLAYER_VMAX = 10.0


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)

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
    
    # TODO: Get loudness of framedata and if loudness isn't enough don't show freqency

    # Estimate fundamental frequency of framedata 
    freq = min(get_frequency(framedata, RECORDER_SAMPLERATE), RECORDER_MAX_FREQ)

    # print(freq)

    plotdata[0] = freq
    plotdata = np.roll(plotdata, -1, axis=0)

    lines[0].set_ydata(plotdata)

    # print('Elapsed: ', time.time() - start)
    return lines


def update_player_plot(frame):
    global player_plot
    global latest_specgram

    while 1:
        try:
            latest_specgram = player_queue.get_nowait()
        except:
            # expect empty queue
            break
    
    # This reqires PLAYER_FRAME_SHIFT > PLAYER_PLOT_INTERVAL
    player_plot[0] = latest_specgram
    player_plot = np.roll(player_plot, -1, axis=0)

    im.set_array(np.transpose(player_plot))

    return im,


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='wav file to play')

    args = parser.parse_args()

    # Recorder
    q = queue.Queue()

    framedata = np.zeros(RECORDER_FRAME_SIZE)
    plotdata = np.zeros(RECORDER_N_FRAMES)

    # TODO: Add Title
    fig1, ax1 = plt.subplots()
    # ax1.set_title("Player spectrogram")

    fig2, ax2 = plt.subplots()
    # ax2.set_title("Recorder frequency")
    
    # Initalization of Player Plot
    # TODO: 補助線入れたい
    lines = ax1.plot(plotdata)

    # TODO: (-INTERVAL * N_FRAMES, 0) に直したい
    ax1.axis((0, 20, 0, RECORDER_MAX_FREQ))
    ax1.grid(which="major", axis="y", color="gray", alpha=0.7, linestyle="-", linewidth=0.5)

    # Initialization of Recorder Plot
    # 0 -> vmin
    player_plot = np.zeros([PLAYER_N_FRAMES, PLAYER_LENFREQ])
    latest_specgram = np.zeros(PLAYER_LENFREQ)
    
    extent = [-PLAYER_N_FRAMES * (PLAYER_PLOT_INTERVAL / 1000.0), 0, 0.0, PLAYER_LIM_FREQ]

    im = ax2.imshow(np.transpose(player_plot), cmap='hot', origin='lower', aspect='auto', extent=extent, vmin=PLAYER_VMIN, vmax=PLAYER_VMAX)

    # TODO: designate device
    stream = sd.InputStream(channels=RECORDER_N_CHANNELS, samplerate=RECORDER_SAMPLERATE, callback=callback)
    ani1 = FuncAnimation(fig1, update_plot, interval=RECORDER_PLOT_INTERVAL, blit=True)
    ani2 = FuncAnimation(fig2, update_player_plot, interval=PLAYER_PLOT_INTERVAL, blit=True)

    player_queue = multiprocessing.Queue()

    p = multiprocessing.Process(target=player_main, args=(args.filename, player_queue))

    p.start()

    with stream:
        plt.show()
