##iimports
from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar, Label,IntVar
import tkinter
from customtkinter import CTkButton, CTkLabel, CTk, CTkEntry, CTkOptionMenu
import ffmpeg  
from concurrent.futures import ThreadPoolExecutor, Executor
from multiprocessing.pool import ThreadPool, Pool
import ntpath

from constants import Constants


class ClipperFrame(Frame):
    
    def __init__(self, root):
        super().__init__(root)
        self.acceptable_file_list = ["MP3","WAV"]
        self.file_list = " ".join(self.acceptable_file_list).lower()
        self.clip_number_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.num_clips = IntVar()
        self.num_clips.set(2)
        self.clip_file_path =''
        #***********FRAME BODY************/
        self.root = root
        self.main_label = CTkLabel(
            self, text="Clipper", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.clip_label = CTkLabel(self, text=f"Clip your audio and video files", text_font=("Montserrat", 15),
                                   wraplength=900)
        self.clip_label.grid(row=1, column=0, columnspan=2)

        self.select_files_btn = CTkButton(self, text="Select File", fg_color=Constants.grey,
                                          command=lambda: self._manage_btns("select_file"))
        self.select_files_btn.grid(row=2, column=0, pady=5)
        
        self.num_clips_entry = CTkOptionMenu(self, variable = self.num_clips ,values=self.clip_number_list)
        self.num_clips_entry.grid(row=3, column=0, columnspan=2, pady=10)

        self.download_video_btn = CTkButton(self, text="Clip selected", fg_color=Constants.grey,
                                            command=lambda: self._manage_btns('start_clipping'))

        self.download_video_btn.grid(row=4, column=0, pady=(0, 10))

    def _manage_btns(self,command):
        if command=="select_file":
            self._reset_vars()
            self._upload_files()
        elif command=="start_clipping":
            self._clip_file()
            pass
        pass

    def _upload_files(self):
        file = filedialog.askopenfile(
            mode="r", filetypes=[("video files", self.file_list)])
        if file == "":
            return
        self.clip_file_path = file.name
        self.file_save_directory = ntpath.dirname(self.clip_file_path)

    def _clip_file(self):
        if self.clip_file_path =='':
            messagebox.showerror("No files", "No file selected to clip")
        
        if not messagebox.askokcancel('Save directory',"Save in current directory?"):
            self.file_save_directory = filedialog.askdirectory()
        file_name = ntpath.basename(self.clip_file_path)

        print(f"{self.file_save_directory},{file_name}")
                
        num_of_clips = int(self.num_clips.get())
        for index,num in enumerate(range(num_of_clips),start=1):
            print(f"{index}.{file_name}")

    def _reset_vars(self):
        self.clip_file_path =''
        pass