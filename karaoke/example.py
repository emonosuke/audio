import matplotlib.pyplot as plt
import numpy as np

import multiprocessing
import threading

#multiprocessing.freeze_support() # <- may be required on windows

def plot(datax, datay):
    x = datax
    y = datay**2
    plt.scatter(x, y)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    p = threading.Thread(target=plot, args=(1, 1))
    p.start()

    datax = 1
    datay = 2
    x = datax
    y = datay**2
    plt.scatter(x, y)
    plt.show()
