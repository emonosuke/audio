"""
This is the Entry point for karaoke system.
"""
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import queue
from helpers import get_frequency, get_loudness
import time
import argparse
import multiprocessing
import math
from player import player_main
from player import PLAYER_SAMPLERATE, PLAYER_LENFREQ, PLAYER_LIM_FREQ

RECORDER_SAMPLERATE = 16000
RECORDER_N_CHANNELS = 1

RECORDER_FRAME_DURATION = 0.1
RECORDER_FRAME_SIZE = int(RECORDER_SAMPLERATE * RECORDER_FRAME_DURATION)
RECORDER_N_FRAMES = 20

RECORDER_MAX_FREQ = 500

PLAYER_N_FRAMES = 100

RECORDER_PLOT_INTERVAL = 50 
PLAYER_PLOT_INTERVAL = 20

RECORDER_MAX_VOL = 30
RECORDER_MIN_VOL = -30


def callback(indata, frames, time, status):
    """
    Get InputStream from Microphone
    """
    if status:
        print(status, file=sys.stderr)

    recorder_queue.put(indata)


def update_plot(frame):
    """
    Update Recorder plot(Frequency and Volume)
    """
    global plotdata, framedata
    global plotvol
    while True:
        try:
            data = recorder_queue.get_nowait()
        except queue.Empty:
            break

        shift = len(data)

        if len(data) >= RECORDER_FRAME_SIZE:
            framedata = data[-RECORDER_FRAME_SIZE:].flatten()
        else:
            framedata[:shift] = data.flatten()
            framedata = np.roll(framedata, -shift, axis=0)
    
    # Get loudness of framedata(and if loudness isn't enough don't show freqency)
    ld = get_loudness(framedata)

    # Estimate fundamental frequency of framedata 
    freq = min(get_frequency(framedata, RECORDER_SAMPLERATE), RECORDER_MAX_FREQ)
    
    global args
    if ld < args.thresold:
        plotdata[0] = math.nan
    else:
        plotdata[0] = freq
    
    plotvol[0] = max(min(ld, RECORDER_MAX_VOL), RECORDER_MIN_VOL)
    
    plotdata = np.roll(plotdata, -1, axis=0)
    plotvol = np.roll(plotvol, -1, axis=0)

    l1[0].set_ydata(plotdata)
    l3[0].set_ydata(plotvol)

    return (l1 + l3)


def update_player_plot(frame):
    """
    Update player plot(Spectrogram)
    """
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

    # Optional Arguments
    parser.add_argument('vmin', nargs='?', type=float, default=-10.0, 
                        help='colormap minimum value of spectrogram')
    parser.add_argument('vmax', nargs='?', type=float, default=10.0, 
                        help='colormap maximum value of spectrogram')
    parser.add_argument('thresold', nargs='?', type=float, default=-20.0, 
                        help='thresold to plot frequency')

    args = parser.parse_args()

    recorder_queue = queue.Queue()

    framedata = np.zeros(RECORDER_FRAME_SIZE)
    plotdata = np.zeros(RECORDER_N_FRAMES)
    plotvol = np.zeros(RECORDER_N_FRAMES)

    fig1, (ax1, ax3) = plt.subplots(nrows=2, figsize=(6, 6))
    plt.subplots_adjust(hspace=0.3)

    ax1.set_title("Frequency")
    ax3.set_title("Volume")

    fig2, ax2 = plt.subplots()
    ax2.set_title("Spectrogram")
    
    # Initalization of Player Plot
    l1 = ax1.plot(plotdata)
    l3 = ax3.plot(plotvol)

    ax1.axis((0, RECORDER_N_FRAMES, 0, RECORDER_MAX_FREQ))
    ax1.grid(which="major", axis="y", color="gray", alpha=0.7, linestyle="-", linewidth=0.5)

    ax3.axis((0, RECORDER_N_FRAMES, RECORDER_MIN_VOL, RECORDER_MAX_VOL))
    ax3.grid(which="major", axis="y", color="gray", alpha=0.7, linestyle="-", linewidth=0.5)

    # Initialization of Recorder Plot
    player_plot = np.zeros([PLAYER_N_FRAMES, PLAYER_LENFREQ])
    latest_specgram = np.zeros(PLAYER_LENFREQ)
    
    extent = [-PLAYER_N_FRAMES * (PLAYER_PLOT_INTERVAL / 1000.0), 0, 0.0, PLAYER_LIM_FREQ]

    im = ax2.imshow(np.transpose(player_plot), cmap='hot', origin='lower', aspect='auto', extent=extent, vmin=args.vmin, vmax=args.vmax)

    stream = sd.InputStream(channels=RECORDER_N_CHANNELS, samplerate=RECORDER_SAMPLERATE, callback=callback)
    ani1 = FuncAnimation(fig1, update_plot, interval=RECORDER_PLOT_INTERVAL, blit=True)
    ani2 = FuncAnimation(fig2, update_player_plot, interval=PLAYER_PLOT_INTERVAL, blit=True)

    player_queue = multiprocessing.Queue()

    p = multiprocessing.Process(target=player_main, args=(args.filename, player_queue))

    p.start()

    with stream:
        plt.show()
