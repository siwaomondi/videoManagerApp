from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter

from customtkinter import CTkButton, CTkLabel, CTk
class FileExistsError(Exception):
    pass

from apps.converter.converter_frame import ConverterFrame
from apps.ytDownload.yt_download_frame import YtDownloaderFrame
from apps.home.home_frame import HomeFrame
from constants import Constants

class VideoManager:
    def __init__(self):
        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = CTk()
        self.root.iconbitmap( Constants.app_icon)
        self.root.geometry(f"{800}x{600}")
        self.root.minsize(800, 600)
        self.root.maxsize(800, 600)
        self.root.config(  # padx=50, pady=50,
            bg=Constants.blue)

        self.rx = self.root.winfo_x()
        self.ry = self.root.winfo_y()

        #/**********FRAMES***************/
        self.mp4ConverterFrame = ConverterFrame(
            root=self.root
        )
        self.ytDownloadFrame = YtDownloaderFrame(root=self.root)
        self.home_frame = HomeFrame(root =self.root,open_command=self._open_select_frame,mp4Frame=self.mp4ConverterFrame,yTFrame=self.ytDownloadFrame)



        # HOME FRAME
        self.home_frame.pack(fill="both", expand=True, padx=30, pady=(10, 10))
        self.list_of_frames = [self.home_frame,self.ytDownloadFrame,self.mp4ConverterFrame]

        # MAIN MENU
        self.main_menu = Menu(self.root)
        self.root.configure(menu=self.main_menu)

        
        # /**********MENUS**********/
        # File menu
        self.file_menu = Menu(self.main_menu)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Home", command=lambda:self._open_select_frame(self.home_frame))
        self.file_menu.add_command(label="Convert", command=lambda:self._open_select_frame(self.mp4ConverterFrame))
        self.file_menu.add_command(label="YTDownload", command=lambda:self._open_select_frame(self.ytDownloadFrame))
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        

        # MAINLOOP
        self._open_select_frame(self.home_frame)
        self.root.mainloop()
    def _hide_all_frames(self):      
        for frame in self.list_of_frames:
            frame.pack_forget()
            
    def _open_select_frame(self,frame):
        self._hide_all_frames()
        frame.config(bg=Constants.blue)
        frame.pack(fill="both", expand=1, padx=30, pady=(10, 10))
