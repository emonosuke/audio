import multiprocessing
import time

from other_proc import incr


q = multiprocessing.Queue()
p = multiprocessing.Process(target=incr, args=(q,))

p.start()

while q:
    top = q.get()
    print(top)

p.join()
