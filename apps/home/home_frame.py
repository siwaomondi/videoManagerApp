from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter

from customtkinter import CTkButton, CTkLabel, CTk
from constants import Constants

class HomeFrame(Frame):
    def __init__(self,root,open_command,mp4Frame,yTFrame,clipperFrame):
        super().__init__(root)


        #***********FRAME BODY************/
        self.root = root
        self.root.title("VIDMAN")
        
        self.main_home_label = CTkLabel(
            self, text="Welcome", font=Constants.title_font)
        self.main_home_label.pack(pady=(0, 10))

        self.home_description_label = CTkLabel(self,
                                          text=f"Please select service below:",
                                          font=Constants.instuction_font, wraplength=900)
        self.home_description_label.pack(pady=(0, 10))

        self.mp4_convert_btn = CTkButton(self, text="Convert video to audio", **Constants.btn_colour,
                                          command=lambda:open_command(mp4Frame))
        self.mp4_convert_btn.pack(pady=(0, 10))
        self.yt_download_btn = CTkButton(self, text="Yt Download",**Constants.btn_colour,
                                          command=lambda:open_command(yTFrame),)
        self.yt_download_btn.pack(pady=(0, 10))
        self.clipper_btn = CTkButton(self, text="Clipper", **Constants.btn_colour,
                                          command=lambda:open_command(clipperFrame))
        self.clipper_btn.pack(pady=(0, 10))

