import time
from tkinter import *
class MyApp:
    def __init__(self, parent):
        self.myParent = parent  ### (7) remember my parent, the root
        self.myContainer1 = Frame(parent)
        self.myContainer1.pack()
        self.button1 = Button(self.myContainer1)
        self.button1.configure(text="Button")
        self.button1.pack()
        self.button1.bind("<Button-1>", self.button1Click)
        self.lbl = Label(self.myContainer1)
        self.lbl.pack()
        self.button2 = Button(self.myContainer1)
        self.button2.configure(text="Quit", background="red")
        self.button2.pack()
        self.button2.bind("<Button-1>", self.button2Click)
    def button1Click(self, event):    ### (3)
        # expensive process here
        # simulated by time.sleep
        self.lbl.configure(text='Running command...')
        time.sleep(4)
        self.lbl.configure(text='Finished running command...')
    def button2Click(self, event):  ### (5)
        self.myParent.destroy()     ### (6)
root = Tk()

myapp = MyApp(root)
root.mainloop()
