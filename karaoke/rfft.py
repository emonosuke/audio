import numpy as np

arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

res = np.fft.fft(arr)

print(len(res))
