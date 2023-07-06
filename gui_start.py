import customtkinter as ctk
from tkinter import *
#from PIL import ImageTk, Image


class splashscreen(ctk.CTkToplevel):
    def __init__(self):
        ctk.CTkToplevel.__init__(self)
        print('test')

        self.update()
