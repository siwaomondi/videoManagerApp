##iimports
from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar, Label
import tkinter
from customtkinter import CTkButton, CTkLabel, CTk, CTkEntry, CTkOptionMenu

from pytube import YouTube
import pytube.exceptions as pytExcept
from pytube import Playlist
from threading import Thread, Event
import threading
import asyncio

from concurrent.futures import ThreadPoolExecutor, Executor
from multiprocessing.pool import ThreadPool, Pool
import time

from constants import Constants


class ClipperFrame(Frame):
    
    def __init__(self, root):
        super().__init__(root)
        


        #***********FRAME BODY************/
        self.root = root
        self.main_label = CTkLabel(
            self, text="Clipper", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.clip_label = CTkLabel(self, text=f"Clip your audio and video files", text_font=("Montserrat", 15),
                                   wraplength=900)
        self.clip_label.grid(row=1, column=0, columnspan=2)

        self.link_entry = CTkEntry(self)
        self.link_entry.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

        self.download_video_btn = CTkButton(self, text="Download video(s)", fg_color=Constants.grey,
                                            command=lambda: self._manage_btns('start_video_download'))

        self.download_video_btn.grid(row=4, column=0, pady=(0, 10))

        self.download_audio_btn = CTkButton(self, text="Download audio(s)", fg_color=Constants.grey,
                                            command=lambda: self._manage_btns('start_audio_download'))

        self.download_audio_btn.grid(row=4, column=1)


    def _manage_btns(self):
        pass
