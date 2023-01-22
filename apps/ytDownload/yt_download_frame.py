from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter

from customtkinter import CTkButton, CTkLabel, CTk
from constants import Constants
class YtDownloaderFrame(Frame):
    def __init__(self,root):
        super().__init__(root)
        self.root = root
        self.root.title("YT_Download | VIDMAN")
        self.main_label = CTkLabel(
            self, text="Welcome", text_font=("Montserrat", 30, "bold"))
        self.main_label.pack()

