from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter

from customtkinter import CTkButton, CTkLabel, CTk
from constants import Constants

class HomeFrame(Frame):
    def __init__(self,root,open_command,mp4Frame,yTFrame):
        super().__init__(root)
        self.root = root
        self.root.title("VIDMAN")
        
        self.main_home_label = CTkLabel(
            self, text="Welcome", text_font=("Montserrat", 30, "bold"))
        self.main_home_label.pack(pady=(0, 10))

        self.home_description_label = CTkLabel(self,
                                          text=f"Please select service below:",
                                          text_font=("Montserrat", 15), wraplength=900)
        self.home_description_label.pack(pady=(0, 10))

        self.mp4ConvertBtn = CTkButton(self, text="Convert video to audio", fg_color=Constants.grey,
                                          command=lambda:open_command(mp4Frame))
        self.mp4ConvertBtn.pack(pady=(0, 10))
        self.ytDownloadBtn = CTkButton(self, text="Yt Download", fg_color=Constants.grey,
                                          command=lambda:open_command(yTFrame))
        self.ytDownloadBtn.pack(pady=(0, 10))

