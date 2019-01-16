from player import Player
from player import PLAYER_N_PLOTS, PLAYER_FRAME_SHIFT
from recorder import Recorder
from recorder import RECORDER_N_FRAMES, RECORDER_MAX_FREQ
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import argparse
import subprocess


def update_player_plot(*args):
    player_plot = p.update()
    player_im.set_array(np.transpose(player_plot))

    return player_im,


def update_recorder_plot(*args):
    recorder_plot = r.update()
    rec_lines[0].set_ydata(recorder_plot)

    return rec_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='wav file to play')

    args = parser.parse_args()

    p = Player(filename=args.filename)

    r = Recorder()

    player_plot = p.plotdata
    recorder_plot = r.plotdata

    # For player's plot
    fig1, ax1 = plt.subplots()

    # For recorder's plot
    fig2, ax2 = plt.subplots()
    
    extent = [0.0, PLAYER_N_PLOTS * PLAYER_FRAME_SHIFT, 0.0, p.samplerate / 2]
    player_im = ax1.imshow(np.transpose(player_plot), cmap='hot', origin='lower', aspect='auto', extent=extent, vmin=p.specmin, vmax=p.specmax)

    # TODO: 補助線入れたい
    rec_lines = ax2.plot(recorder_plot)
    ax2.axis((0, RECORDER_N_FRAMES, 0, RECORDER_MAX_FREQ))

    ani1 = FuncAnimation(fig1, update_player_plot, interval=100, blit=True)
    ani2 = FuncAnimation(fig2, update_recorder_plot, interval=100, blit=True)

    r = Recorder()

    r.start()

    p.play()

    plt.show()
