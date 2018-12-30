import os
import math
import numpy as np
import scipy.io.wavfile
from specgram import FRAME_DURATION, FRAME_SHIFT
from recog_helper import get_cepstrum, calc_likelihood

ROOTDIR = os.getcwd()
DATADIR = os.path.join(ROOTDIR, 'train')

PATH_A = os.path.join(DATADIR, 'a.wav')
PATH_I = os.path.join(DATADIR, 'i.wav')
PATH_U = os.path.join(DATADIR, 'u.wav')
PATH_E = os.path.join(DATADIR, 'e.wav')
PATH_O = os.path.join(DATADIR, 'o.wav')

VOWEL = {0: 'a', 1: 'i', 2: 'u', 3: 'e', 4: 'o'}


class VowelClassifier(object):
    """
    description of VowelClassifier
    """
    def __init__(self):
        """
        Get cepstrum from train/a.wav, i.wav, u.wav, e.wav, o.wav
        and caluculate mean, std of each vowel
        """
        sampling_rate, aw = scipy.io.wavfile.read(PATH_A)
        _, iw = scipy.io.wavfile.read(PATH_I)
        _, uw = scipy.io.wavfile.read(PATH_U)
        _, ew = scipy.io.wavfile.read(PATH_E)
        _, ow = scipy.io.wavfile.read(PATH_O)

        aw = aw / 32768.0
        iw = iw / 32768.0
        uw = uw / 32768.0
        ew = ew / 32768.0
        ow = ow / 32768.0

        # a, i, u, e, o に対応するケプストラム
        cep_a, cep_i, cep_u, cep_e, cep_o = [], [], [], [], []

        left = 0
        right = FRAME_DURATION * sampling_rate

        while right < len(aw):
            cep_a.append(get_cepstrum(aw, sampling_rate, left, right))
            cep_i.append(get_cepstrum(iw, sampling_rate, left, right))
            cep_u.append(get_cepstrum(uw, sampling_rate, left, right))
            cep_e.append(get_cepstrum(ew, sampling_rate, left, right))
            cep_o.append(get_cepstrum(ow, sampling_rate, left, right))

            left += FRAME_SHIFT * sampling_rate
            right += FRAME_SHIFT * sampling_rate
        
        self.__means = np.mean([cep_a, cep_i, cep_u, cep_e, cep_o], axis=1)
        self.__stds = np.std([cep_a, cep_i, cep_u, cep_e, cep_o], axis=1)

    def predict(self, waveform, sampling_rate):
        taxis = []
        recogs = []

        left = 0
        right = FRAME_DURATION * sampling_rate

        while right < len(waveform):
            taxis.append((left + right) / (2 * sampling_rate))

            cep = get_cepstrum(waveform, sampling_rate, left, right)

            lh = []
            for i in range(5):
                lh.append(calc_likelihood(cep, self.__means[i], self.__stds[i]))

            recogs.append(VOWEL[np.argmax(lh)])

            left += FRAME_SHIFT * sampling_rate
            right += FRAME_SHIFT * sampling_rate

        # FOR DEBUG
        print(taxis)
        print(recogs)

        return taxis, recogs
