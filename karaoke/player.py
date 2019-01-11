import sys
import wave
import time
import numpy as np
import pyaudio
from optparse import OptionParser
from queue import Queue

BUF_SIZE = 8192

FRAME_DURATION = 0.1
FRAME_RATE = 10.0


class Player():
    """
    Attributes
    ----------
    buf_size : 
        再生バッファのサイズ[bytes]
    frame_duration : 
        1フレームの長さ[秒]
    frame_rate : 
        1秒あたりのフレーム数
    """
    def __init__(self, 
                 filename,
                 buf_size=BUF_SIZE, 
                 frame_duration=FRAME_DURATION, 
                 frame_rate=FRAME_RATE, 
                 verbose=False):
        self.wave_read = wave.open(filename, 'rb')
        self.buf_size = buf_size
        self.frame_rate = frame_rate
        self.verbose = verbose

        self.sampling_rate = self.wave_read.getframerate()
        self.nsamples = self.wave_read.getnframes()

        self.pa = pyaudio.PyAudio()
        self.out = self.pa.open(
            format=self.pa.get_format_from_width(self.wave_read.getsampwidth()),
            channels=self.wave_read.getnchannels(),
            rate=self.sampling_rate,
            output=True
        )

        self.buf = np.ndarray(self.buf_size)
        self.buf_pos = 0
        
        self.frame_size = int(self.sampling_rate * frame_duration)
        self.frame_shift = int(self.sampling_rate / self.frame_rate)
        self.frame = np.zeros(self.frame_size)
        self.window = np.hanning(self.frame_size)
        self.queue = Queue()

    def play(self, size):
        buf_remain = self.buf_size - self.buf_pos

        if buf_remain >= size:
            buf_pos0 = self.buf_pos
            self.buf_pos += size
            return self.buf[buf_pos0:self.buf_pos]
        else:
            frame = np.ndarray(size)
            
            frame[:buf_remain] = self.buf[self.buf_pos:]
            frame_remain = size - buf_remain

            while frame_remain > self.buf_size:
                d = self.wave_read.readframes(self.buf_size)
                self.out.write(d)
                w = np.fromstring(d, dtype=int) * (2.0 ** 15)
                frame[-frame_remain:-frame_remain + self.buf_size] = w
                frame_remain -= self.buf_size
            
            if frame_remain > 0:
                d = self.wave_read.readframes(self.buf_size)
                self.out.write(d)
                w = np.fromstring(d, dtype=int) * (2.0 ** 15)
                frame[-frame_remain:] = self.buf[:frame_remain]
                self.buf_pos -= frame_remain
            
            return frame
    

    def run(self):
        t0 = time.time()
        nsamples_remain = self.nsamples

        while nsamples_remain > 0:
            t1 = time.time()
            
            frame0 = self.play(self.frame_shift)

            if self.frame_size > self.frame_shift:
                self.frame[:self.frame_shift] = frame0[-self.frame_shift:]
                self.frame = np.roll(self.frame, -self.frame_shift)
            else:
                self.frame = frame0
            
            wframe = self.frame * self.window
            self.queue.put(wframe)
            nsamples_remain -= self.frame_shift
    

def main():
    parser = OptionParser(usage='usage: %prog [options] WAVFILE')
    parser.add_option('-v',
                        '--verbose', 
                        dest='verbose', 
                        action='store_true', 
                        default=False,
                        help='verbose output')
    (options, args) = parser.parse_args()
    verbose = options.verbose

    if len(args) == 0:
        print('no input files.')
        sys.exit()
    
    filename = args[0]
    p = Player(filename, verbose=verbose)
    p.run()

if __name__ == '__main__':
    main()
