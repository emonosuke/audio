import sys
import wave
import numpy as np
import pyaudio
import time
from optparse import OptionParser
from threading import Thread
from queue import Queue

RECORDER_NCHANNELS = 1
RECORDER_SAMPLING_RATE = 16000
RECORDER_DURATION = 10.0
RECORDER_FILENAME = "output.wav"
RECORDER_SAMPLE_WIDTH = 2  # bytes
RECORDER_BUF_SIZE = 4000

FRAME_DURATION = 0.1  # 1フレームの長さ[秒]
FRAME_RATE = 10.0  # 1秒あたりのフレーム数


class Recorder(Thread):
    def __init__(self,
                 sampling_rate=RECORDER_SAMPLING_RATE,
                 duration=RECORDER_DURATION,
                 filename=RECORDER_FILENAME,
                 buf_size=RECORDER_BUF_SIZE,
                 frame_duration=FRAME_DURATION,
                 frame_rate=FRAME_RATE,
                 verbose=False):
        super(Recorder, self).__init__()

        self.sampling_rate = sampling_rate
        self.duration = duration
        self.filename = filename
        self.buf_size = buf_size
        self.frame_duration = frame_duration
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / self.frame_rate
        self.verbose = verbose

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(RECORDER_SAMPLE_WIDTH),
            channels=RECORDER_NCHANNELS,
            rate=self.sampling_rate,
            frames_per_buffer=self.buf_size,
            input=True
        )
        self.wav_write = wave.open(filename, 'wb')
        self.wav_write.setnchannels(RECORDER_NCHANNELS)
        self.wav_write.setsampwidth(RECORDER_SAMPLE_WIDTH)
        self.wav_write.setframerate(self.sampling_rate)

        self.frame_size = int(self.sampling_rate * self.frame_duration)
        self.frame_shift = int(self.sampling_rate * self.frame_interval)
        self.frame = np.zeros(self.frame_size)
        self.window = np.hanning(self.frame_size)
        self.frame_replace = min(self.frame_size, self.frame_shift)

        self.pcount = 0
        self.buf = np.ndarray(self.buf_size)
        self.buf_pos = self.buf_size
        self.queue = Queue()

    def record(self, size):
        buf_remain = len(self.buf) - self.buf_pos
        if buf_remain >= size:
            buf_pos0 = self.buf_pos
            self.buf_pos += size
            return self.buf[buf_pos0:self.buf_pos]
        else:
            frame = np.ndarray(size)
            frame[:buf_remain] = self.buf[self.buf_pos:]
            frame_remain = size - buf_remain
            while frame_remain > self.buf_size:
                buf = self.stream.read(self.buf_size)
                self.wav_write.writeframes(buf)
                self.pcount += 1
                w = np.fromstring(buf, dtype=np.int16) * (2.0 ** -15)
                frame[-frame_remain:-frame_remain + self.buf_size] = w
                frame_remain -= self.buf_size
            if frame_remain > 0:  # 0 < frame_remain < self.buf_size
                buf = self.stream.read(self.buf_size)
                self.wav_write.writeframes(buf)
                self.pcount += 1
                w = np.fromstring(buf, dtype=np.int16) * (2.0 ** -15)
                self.buf[:len(w)] = w[:]
                frame[-frame_remain:] = self.buf[:frame_remain]
                self.buf_pos = frame_remain
            return frame
    
    def run(self):
        nsamples_remain = int(self.sampling_rate * self.duration)
        while nsamples_remain > 0:
            frame0 = self.record(self.frame_shift)
            nsamples_remain -= len(frame0)
            if(self.frame_size > self.frame_shift):
                self.frame[:self.frame_shift] = frame0[-self.frame_shift]
                self.frame = np.roll(self.frame, -self.frame_shift)
            else:
                self.frame = frame0
            wframe = self.frame * self.window

            self.queue.put(wframe)


def main():
    parser = OptionParser()
    parser.add_option('-v',
                      '--verbose',
                      dest='verbose',
                      action='store_true',
                      default=False,
                      help='verbose output')
    (options, args) = parser.parse_args()

    """
    r = Recorder(
        duration=RECORDER_DURATION,
        sampling_rate=RECORDER_SAMPLING_RATE,
        filename=args[0] if len(args) > 0 else RECORDER_FILENAME,
        frame_rate=FRAME_RATE,
        frame_duration=FRAME_DURATION,
        verbose=options.verbose
    )
    """
    r = Recorder()

    r.start()

if __name__ == '__main__':
    main()
