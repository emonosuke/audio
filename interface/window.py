import os
import sys
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import scipy.io.wavfile


# 参照ボタンのイベント
# refbutton クリック時の処理
def refbutton_clicked():
    fTyp = [(".wav File Only", "*.wav")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    filepath = filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
    file_target.set(filepath)


def openbutton_clicked(sp, canvas):
    # ここで参照ファイル名が取得できている
    # messagebox.showinfo('Information', file_target.get())

    def update_graph():
        sampling_rate, waveform = scipy.io.wavfile.read(file_target.get())

        times = np.arange(len(waveform)) / sampling_rate
        waveform = waveform / 32768.0

        sp.cla()
        sp.plot(times, waveform, linewidth=0.5, color='darkorange')

        canvas.draw()
    
    return update_graph


if __name__ == '__main__':
    # rootの作成
    root = tkinter.Tk()
    root.title('Audio Analysis GUI')
    # root.resizable(False, False)

    frame1 = ttk.Frame(root, padding=10)
    frame1.grid()

    # 参照ボタンの作成
    refbutton = ttk.Button(root, text='参照', command=refbutton_clicked)
    refbutton.grid(row=0, column=3)

    # 「ファイル」ラベルの作成
    s = tkinter.StringVar()
    s.set('ファイル: ')
    label1 = ttk.Label(frame1, textvariable=s)
    label1.grid(row=0, column=0)

    # 参照ファイルパス表示ラベルの作成
    file_target = tkinter.StringVar()
    file_target_entry = ttk.Entry(frame1, textvariable=file_target, width=50)
    file_target_entry.grid(row=0, column=2)

    frame2 = ttk.Frame(root, padding=(0, 5))
    frame2.grid(row=1)

    frame3 = ttk.Frame(root)
    frame3.grid(row=2)

    fig = Figure(figsize=(5, 4), dpi=100)
    t = np.arange(0, 3, .01)
    sp = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=frame3)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    openbutton = ttk.Button(frame2, text='開く', command=openbutton_clicked(sp, canvas))
    openbutton.pack(side=tkinter.LEFT)
    
    root.mainloop()
