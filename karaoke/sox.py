from multiprocessing import Process
import subprocess
import sys


def playback(filename):
    subprocess.call(['play', filename])

p = Process(target=playback, args=(sys.argv[1],))
p.start()

print("start playing!!")
