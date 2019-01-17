import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


def update1(*args):
    global ax1plot

    ax1plot = np.roll(ax1plot, +1, axis=1)
    print(ax1plot)
    im1.set_array(ax1plot)

    return im1,


def update2(*args):
    global ax2plot

    ax2plot = np.roll(ax2plot, -1, axis=1)
    print(ax2plot)
    im2.set_array(ax2plot)

    return im2,


fig1, ax1 = plt.subplots()

fig2, ax2 = plt.subplots()

ax1plot = [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]
ax2plot = [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]

im1 = ax1.imshow(ax1plot)
im2 = ax2.imshow(ax2plot)

ani1 = FuncAnimation(fig1, update1, interval=100, blit=True)
ani2 = FuncAnimation(fig2, update2, interval=100, blit=True)

plt.show()
