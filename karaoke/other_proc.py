import time


def incr(q):
    cnt = 0
    while 1:
        time.sleep(1)
        q.put(cnt)
        cnt += 1
