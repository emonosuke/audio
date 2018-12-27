import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


# 参照ボタンのイベント
# refbutton クリック時の処理
def refbutton_clicked():
    fTyp = [(".wav File Only", "*.wav")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    filepath = filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
    file_target.set(filepath)


# openbutton クリック時の処理
def openbutton_clicked():
    messagebox.showinfo('Information', file_target.get())


if __name__ == '__main__':
    # rootの作成
    root = Tk()
    root.title('Audio Analysis GUI')
    root.resizable(False, False)

    # Frame1 の作成
    frame1 = ttk.Frame(root, padding=10)
    frame1.grid()

    # 参照ボタンの作成
    refbutton = ttk.Button(root, text='Reference', command=refbutton_clicked)
    refbutton.grid(row=0, column=3)

    # 「ファイル」ラベルの作成
    s = StringVar()
    s.set('ファイル: ')
    label1 = ttk.Label(frame1, textvariable=s)
    label1.grid(row=0, column=0)

    # 参照ファイルパス表示ラベルの作成
    file_target = StringVar()
    file_target_entry = ttk.Entry(frame1, textvariable=file_target, width=50)
    file_target_entry.grid(row=0, column=2)

    # Frame2 の作成
    frame2 = ttk.Frame(root, padding=(0, 5))
    frame2.grid(row=1)

    # Open ボタンの作成
    openbutton = ttk.Button(frame2, text='Open', command=openbutton_clicked)
    openbutton.pack(side=LEFT)

    root.mainloop()
