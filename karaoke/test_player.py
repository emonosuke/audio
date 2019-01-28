"""
This is the test module for player
"""

import multiprocessing
import time
import sys
from player import player_main
from queue import Queue

filename = sys.argv[1]

q = multiprocessing.Queue()
p = multiprocessing.Process(target=player_main, args=(filename, q))

p.start()

while 1:
    time.sleep(1)

    while 1:
        try:
            top = q.get_nowait()
        except:
            # expect empty queue
            break
    
    print("player caller: ", top)

p.join()
