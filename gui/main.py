from specgram import FRAME_DURATION, FRAME_SHIFT, LIM_FREQ
from specgram import predict_fundamentals
from recog import VowelClassifier
import os
import sys
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import math
import numpy as np
import scipy.io.wavfile


def refbutton_clicked():
    """
    When '参照' button clicked, user can select *.wav file from GUI
    """
    fTyp = [(".wav File Only", "*.wav")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    filepath = filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
    file_target.set(filepath)


def openbutton_clicked(sp_spec, sp_recog, canvas_spec, canvas_recog):
    """
    When '開く' button clicked, show spectrogram + fundamental frequency
    and vowel recognition of the file user selected
    This is callback function
    """
    def update_graph():
        sp_spec.cla()
        sp_recog.cla()

        sampling_rate, waveform = scipy.io.wavfile.read(file_target.get())
        waveform = waveform / 32768.0

        # First, show spectrogram

        window_size = int(FRAME_DURATION * sampling_rate)
        window_overlap = int((FRAME_DURATION - FRAME_SHIFT) * sampling_rate)
        window = scipy.hanning(window_size)

        spectrum, freqs, taxis, im = sp_spec.specgram(
            waveform,
            NFFT=window_size,
            Fs=sampling_rate,
            window=window,
            noverlap=window_overlap,
            cmap='hot',
            vmin=None,
            vmax=None
        )

        # Then, show fundamental frequency on spectrogram

        ffs = predict_fundamentals(waveform, sampling_rate)

        # if len(ffs) < len(taxis) append ffs[-1] to ffs
        ffs_fixed = [ffs[i] if i < len(ffs) else ffs[-1] for i in range(len(taxis))]

        sp_spec.plot(taxis, ffs_fixed, color='red', marker='o')

        sp_spec.set_ylim([0, LIM_FREQ])
        sp_spec.set_xlabel('Time [sec]')
        sp_spec.set_ylabel('Frequency [Hz]')

        canvas_spec.draw()

        # Finally, show vowel recognition result under spectrogram

        vc = VowelClassifier()

        taxis, recogs = vc.predict(waveform, sampling_rate)

        # if predicted unvoiced, convert to 'NA'
        recogs = ['NA' if math.isnan(ffs[i]) else recogs[i] for i in range(len(recogs))]

        sp_recog.plot(taxis, recogs, marker='o', linestyle='None')

        canvas_recog.draw()
    
    return update_graph


if __name__ == '__main__':
    root = tkinter.Tk()
    root.title('GUI')
    root.resizable(False, False)

    frame_entry = ttk.Frame(root, padding=10)
    frame_entry.grid()

    refbutton = ttk.Button(root, text='参照', command=refbutton_clicked)
    refbutton.grid(row=0, column=3)

    s = tkinter.StringVar()
    s.set('ファイル: ')
    label = ttk.Label(frame_entry, textvariable=s)
    label.grid(row=0, column=0)

    file_target = tkinter.StringVar()
    file_target_entry = ttk.Entry(frame_entry, textvariable=file_target, width=50)
    file_target_entry.grid(row=0, column=2)

    frame_open = ttk.Frame(root, padding=(0, 5))
    frame_open.grid(row=1)

    # frame_spec > fig_spec > canvas_spec
    frame_spec = ttk.Frame(root)
    frame_spec.grid(row=2)

    fig_spec = Figure(figsize=(6, 4), dpi=100)
    sp_spec = fig_spec.add_subplot(111)

    canvas_spec = FigureCanvasTkAgg(fig_spec, master=frame_spec)
    canvas_spec.draw()
    canvas_spec.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    # frame_recog > fig_recog > canvas_recog
    frame_recog = ttk.Frame(root)
    frame_recog.grid(row=3)

    fig_recog = Figure(figsize=(6, 2), dpi=100)
    sp_recog = fig_recog.add_subplot(111)

    canvas_recog = FigureCanvasTkAgg(fig_recog, master=frame_recog)
    canvas_recog.draw()
    canvas_recog.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    openbutton = ttk.Button(frame_open, text='開く', command=openbutton_clicked(sp_spec, sp_recog, canvas_spec, canvas_recog))
    openbutton.pack(side=tkinter.LEFT)
    
    root.mainloop()
