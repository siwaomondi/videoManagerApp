##iimports
from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar, Label, IntVar
import tkinter
from customtkinter import CTkButton, CTkLabel, CTk, CTkEntry, CTkOptionMenu
from moviepy.editor import VideoFileClip, AudioFileClip
import ntpath
import math
import os
from threading import Thread, Event
from constants import Constants, open_webpage


class ClipperFrame(Frame):

    def __init__(self, root):
        super().__init__(root)
        self.acceptable_audio_file_list = ["MP3", "WAV"]
        self.acceptable_video_file_list = ["MP4", "MOV", "WMV", "AVI", "FLV", "MKV", "WEBM"]
        self.clipping_options = ["Start clipping", "Stop clipping"]
        self.audio_file_list = " ".join(self.acceptable_audio_file_list).lower()
        self.video_file_list = " ".join(self.acceptable_video_file_list).lower()
        self.clip_number_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                                 '18', '19', '20']

        self.num_clips = IntVar()
        self.num_clips.set(2)
        self.clip_file_path = ''
        self.clipping_event = Event()
        self.clipping_cancelled = False
        self.clipped_files = []
        self.file_save_directory = ""
        self.num_clipped = 0
        # ***********FRAME BODY************/
        self.root = root
        self.main_label = CTkLabel(
            self, text="Clipper", font=Constants.title_font)
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.clip_label = CTkLabel(self, text=f"Clip your audio and video files", font=Constants.instuction_font,
                                   wraplength=900)
        self.clip_label.grid(row=1, column=0, columnspan=2)

        self.select_audio_files_btn = CTkButton(self, text="Select Audio File", **Constants.btn_colour,
                                                command=lambda: self._manage_btns("select_audio_file"))
        self.select_audio_files_btn.grid(row=2, column=0, pady=5, padx=(0, 100))

        self.select_video_files_btn = CTkButton(self, text="Select Video file", **Constants.btn_colour,
                                                command=lambda: self._manage_btns("select_video_file"))
        self.select_video_files_btn.grid(row=2, column=1, pady=5)

        self.num_clips_label = CTkLabel(self, text=f"Number of clips", font=Constants.instuction_font)
        self.num_clips_label.grid(row=3, column=0, pady=10, columnspan=2)

        self.num_clips_entry = CTkOptionMenu(self, variable=self.num_clips, values=self.clip_number_list)
        self.num_clips_entry.grid(row=4, column=0, columnspan=2)
        self.clipping_btn = CTkButton(self, text=self.clipping_options[0], **Constants.btn_colour,
                                      command=lambda: self._manage_btns('start_clipping'))

        self.clipping_btn.grid(row=5, column=0, pady=10, columnspan=2)

        self.scroll_frame = Frame(self)
        self.scroll_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.files_textbox = scrolledtext.ScrolledText(
            self.scroll_frame, height=15, bg=Constants.grey, font=Constants.scroll_font
        )
        self.files_textbox.pack(fill="both")
        self.footer_label = Label(
            self,
            bg=Constants.blue,
            text="Clipper by Siwa©",
            font=Constants.footer_font,
        )
        self.footer_label.grid(row=7, column=0, columnspan=2)
        self.footer_label.bind("<ButtonRelease-1>", open_webpage)
        self._render_file_names()

    def _manage_btns(self, command):
        if command in ("select_video_file", "select_audio_file"):
            self._reset_vars()
            if command == "select_video_file":
                self._upload_files("v")
            else:
                self._upload_files("a")
        elif command == "start_clipping":
            self._clip_file()
        elif command == "stop_clipping":
            self.clipping_event.clear()

    def _upload_files(self, mode):
        if mode == "a":
            file = filedialog.askopenfile(
                mode="r", filetypes=[("audio files", self.audio_file_list)])
        elif mode == "v":
            file = filedialog.askopenfile(
                mode="r", filetypes=[("video files", self.video_file_list)])
        if file == "":
            return
        self.clip_file_path = file.name
        self.file_save_directory = ntpath.dirname(self.clip_file_path)

    def _clip_file(self):
        def cancel_message(m):
            if m == "no_file":
                messagebox.showerror("No files", "No file selected to clip")
            elif m == "cancel":
                messagebox.showerror("Cancel", "Clipping canceled")

        if self.clip_file_path == '':
            cancel_message("no_file")
            return
        save = messagebox.askyesnocancel(title='Save directory', message="Save in current directory?")
        if save == None:
            cancel_message("cancel")
            return
        elif not save:
            self.file_save_directory = filedialog.askdirectory()
            if self.file_save_directory == "":
                cancel_message("cancel")
                return

        def clipping_thread():
            self.clipping_event.set()
            self._clipping_check()
            file_name = ntpath.basename(self.clip_file_path)
            file_n, file_ext = os.path.splitext(self.clip_file_path)
            file_name = ntpath.basename(file_n)
            file_type = self._check_extension(file_ext)
            if file_type == "video":
                conversion_file = VideoFileClip(self.clip_file_path)
            elif file_type == "audio":
                conversion_file = AudioFileClip(self.clip_file_path)
            length = conversion_file.duration
            num_of_clips = int(self.num_clips.get())
            sections = self._generate_sections(length, num_of_clips)
            for index, (start, end) in enumerate(sections, start=1):
                if self.clipping_event.is_set():
                    clip_name = f"clip{index} - {file_name}{file_ext}"
                    file_path = ntpath.join(self.file_save_directory, clip_name)
                    clip = conversion_file.subclip(start, end)
                    if file_type == "video":
                        clip.write_videofile(file_path)
                    else:
                        clip.write_audiofile(file_path)
                    self.num_clipped += 1
                    self.clipped_files.append(clip_name)
                    self._render_file_names(clipping=True)
                else:
                    break
            self._end_of_clipping()

        t = Thread(
            target=clipping_thread,
            name=f"Clipping thread"
        )
        t.setDaemon(True)
        print(f"{t.name} has started ...")
        t.start()

    def _clipping_check(self):
        """disable buttons while clipping is ongoing"""
        if self.clipping_event.is_set():
            self.select_audio_files_btn.configure(state=tkinter.DISABLED)
            self.select_video_files_btn.configure(state=tkinter.DISABLED)
            self.clipping_btn.configure(
                text=self.clipping_options[1], command=lambda: self._manage_btns("stop_clipping")
            )
        else:
            self.select_audio_files_btn.configure(state=tkinter.NORMAL)
            self.select_video_files_btn.configure(state=tkinter.NORMAL)
            self.clipping_btn.configure(
                text=self.clipping_options[0], command=lambda: self._manage_btns("start_clipping")
            )

    def _end_of_clipping(self):
        feedback = f"Completed files:{self.num_clipped}/{self.num_clips.get()}"
        self.clipping_event.clear()
        self._clipping_check()
        if self.clipping_cancelled:
            messagebox.showerror(
                "Clipping canceled", f"Clipping canceled.\n\n{feedback}"
            )
        else:
            messagebox.showinfo("Clipping complete", f"All Done.\n\n{feedback}")
        self._render_file_names(completed=True)
        print("Clipping complete")
        self._reset_vars()

    def _check_extension(self, file_ext):
        if file_ext[1:].upper() in self.acceptable_audio_file_list:
            return "audio"
        else:
            return "video"

    def _generate_sections(self, len, num_clips):
        individual_clip = math.ceil(len / num_clips)
        sections = []
        for i in range(num_clips):
            if i == 0:
                start = 0
            else:
                start = i * individual_clip + 1
            if i < num_clips - 1:
                end = (i + 1) * individual_clip
            else:
                end = len
            sections.append((start, end))
        return sections

    def _reset_vars(self):
        self.clip_file_path = ''
        self.clipping_cancelled = False
        self.clipped_files = []
        self.num_clipped = 0
        self.num_clips.set(2)

    def _render_file_names(self, clipping=False, completed=False, ):
        text = ""
        title = f"Save location:    {self.file_save_directory}\n\nNumber of clips:  {self.num_clips.get()}\n\nClipped files:  {self.num_clipped}/{self.num_clips.get()}\n\n"
        reverse_list = self.clipped_files[::-1]
        if clipping:
            v = ""
            for i in reverse_list:
                v += f"*    {i}\n"
            text = f"{title}{v}"
        elif completed:
            msg = "Clipping complete\n\n"
            if self.clipping_cancelled:
                msg = "Clipping cancelled\n\n"
            v = ''
            for i in reverse_list:
                v += f"     *    {i}\n"
            text = title + msg + v
        else:
            text = "YOUR CLIPPED FILES WILL APPEAR HERE"

        self.files_textbox.config(state="normal")
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, text)
        self.files_textbox.config(wrap=WORD, state="disabled")
