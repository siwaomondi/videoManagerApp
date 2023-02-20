##imports
from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar, Label, IntVar, W, E
import tkinter
from customtkinter import CTkButton, CTkLabel, CTk, CTkEntry, CTkOptionMenu
from moviepy.editor import VideoFileClip, AudioFileClip
import ntpath
import math
import os
from threading import Thread, Event
from constants import Constants, open_webpage
import time
import datetime


class ClippingRangeError(Exception):
    pass


class ClipperFrame(Frame):

    def __init__(self, root):
        super().__init__(root)
        self.acceptable_audio_file_list = ["MP3", "WAV"]
        self.acceptable_video_file_list = ["MP4", "MOV", "WMV", "AVI", "FLV", "MKV", "WEBM"]
        self.audio_file_list = " ".join(self.acceptable_audio_file_list).lower()
        self.video_file_list = " ".join(self.acceptable_video_file_list).lower()
        self.clip_number_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
                                 '18', '19', '20']

        self.num_clips = IntVar()
        self.num_clips.set(2)
        self.total_clips = 0
        self.clip_file_path = ''
        self.clipping_event = Event()
        self.clipping_cancelled = False
        self.clipped_files = []
        self.file_save_directory = ""
        self.num_clipped = 0
        self.file_length = 0
        self.formatted_file_length = 0
        self.action_btn = None
        # ***********FRAME BODY************/

        # frame entry constants
        vcmd = (root.register(self._validate_int_entry), "%P")
        clip_entry_settings = {"placeholder_text": "00", "width": 30, "validate": 'all', "validatecommand": vcmd}

        ##mani body
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

        # Clip size frame
        self.main_clips_frame = Frame(self, background=Constants.blue)
        self.main_clips_frame.grid(row=3, column=0, pady=5, columnspan=2)

        self.definite_size_frame = Frame(self.main_clips_frame, background=Constants.blue)
        self.definite_size_frame.grid(row=0, column=0, sticky=W)
        self.num_clips_label = CTkLabel(self.definite_size_frame, text="Number of clips:",
                                        font=Constants.instuction_font)
        self.num_clips_label.grid(row=0, column=0, sticky=W, pady=20)
        self.num_clips_entry = CTkOptionMenu(self.definite_size_frame, variable=self.num_clips,
                                             values=self.clip_number_list, width=80)
        self.num_clips_entry.grid(row=0, column=1, sticky=E)

        self.size_of_clips_label = CTkLabel(self.definite_size_frame, text="Size of clip[hrs:min:sec]:",
                                            font=Constants.instuction_font)
        self.size_of_clips_label.grid(row=1, column=0, sticky=W)
        self.size_of_clips_frame = Frame(self.definite_size_frame, background=Constants.blue)
        self.size_of_clips_frame.grid(row=1, column=1, sticky=E)
        self.size_of_clips_hr_entry = CTkEntry(self.size_of_clips_frame, **clip_entry_settings)
        self.size_of_clips_hr_entry.grid(row=0, column=0)
        self.size_of_clips_min_entry = CTkEntry(self.size_of_clips_frame, **clip_entry_settings)
        self.size_of_clips_min_entry.grid(row=0, column=1)
        self.size_of_clips_sec_entry = CTkEntry(self.size_of_clips_frame, **clip_entry_settings)
        self.size_of_clips_sec_entry.grid(row=0, column=2)

        # Range frame
        self.start_clip_frame = Frame(self.definite_size_frame, background=Constants.blue)
        self.start_clip_frame.grid(row=2, column=0, pady=20, padx=(0, 20))
        self.start_clip_label = CTkLabel(self.start_clip_frame, text="Start time:", font=Constants.instuction_font)
        self.start_clip_label.grid(row=0, column=0)
        self.start_hour_entry = CTkEntry(self.start_clip_frame, **clip_entry_settings)
        self.start_hour_entry.grid(row=0, column=1)
        self.start_min_entry = CTkEntry(self.start_clip_frame, **clip_entry_settings)
        self.start_min_entry.grid(row=0, column=2)
        self.start_sec_entry = CTkEntry(self.start_clip_frame, **clip_entry_settings)
        self.start_sec_entry.grid(row=0, column=3)

        self.end_clip_frame = Frame(self.definite_size_frame, background=Constants.blue)
        self.end_clip_frame.grid(row=2, column=1)
        self.end_clip_label = CTkLabel(self.end_clip_frame, text="End time:", font=Constants.instuction_font)
        self.end_clip_label.grid(row=0, column=0)
        self.end_hour_entry = CTkEntry(self.end_clip_frame, **clip_entry_settings)
        self.end_hour_entry.grid(row=0, column=1)
        self.end_min_entry = CTkEntry(self.end_clip_frame, **clip_entry_settings)
        self.end_min_entry.grid(row=0, column=2)
        self.end_sec_entry = CTkEntry(self.end_clip_frame, **clip_entry_settings)
        self.end_sec_entry.grid(row=0, column=3)

        # clipping btns
        side_padding = {"padx": (40, 0)}
        self.clipping_size_btn = CTkButton(self.definite_size_frame, text="Clip size",
                                           **Constants.btn_colour,
                                           command=lambda: self._manage_btns('clip_size'))
        self.clipping_size_btn.grid(row=1, column=2, **side_padding)
        self.clipping_num_btn = CTkButton(self.definite_size_frame, text="Clip number",
                                          **Constants.btn_colour,
                                          command=lambda: self._manage_btns('clip_number'))
        self.clipping_num_btn.grid(row=0, column=2, **side_padding)
        self.clipping_range_btn = CTkButton(self.definite_size_frame, text="Clip range", **Constants.btn_colour,
                                            command=lambda: self._manage_btns('clip_range'))
        self.clipping_range_btn.grid(row=2, column=2, **side_padding)

        self.clipping_btns_list = [{"btn": self.clipping_range_btn, "text": "Clip range", "command": "clip_range"},
                                   {"btn": self.clipping_size_btn, "text": "Clip size", "command": "clip_size"},
                                   {"btn": self.clipping_num_btn, "text": "Clip number", "command": "clip_number"}]

        # Scroll Frame
        self.scroll_frame = Frame(self)
        self.scroll_frame.grid(row=4, column=0, columnspan=2, pady=10)

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
        self.footer_label.grid(row=5, column=0, columnspan=2)
        self.footer_label.bind("<ButtonRelease-1>", open_webpage)
        self._render_file_names()

    def _validate_int_entry(self, P):
        """validate int characters to entry widgets and limit max len to 2"""

        if str.isdigit(P) and len(P) <= 2 or P == "":
            return True
        else:
            return False

    def _manage_btns(self, command):
        if command in ("select_video_file", "select_audio_file"):
            self._reset_vars()
            if command == "select_video_file":
                self._upload_files("v")
            else:
                self._upload_files("a")
        elif command == "clip_number":
            self.action_btn = self.clipping_num_btn
            self._clip_file("number")
        elif command == "clip_size":
            self.action_btn = self.clipping_size_btn
            self._clip_file("size")
        elif command == "clip_range":
            self.action_btn = self.clipping_range_btn
            self._clip_file("range")
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
        self._get_file_details()
        self._render_file_names(file_select=True)

    def _clip_file(self, clip_type):
        # TODO add progressbar to clipping
        def cancel_message(m):
            if m == "no_file":
                messagebox.showerror("No files", "No file selected to clip")
            elif m == "cancel":
                messagebox.showerror("Cancel", "Clipping canceled")
            elif m == "invalid_range":
                messagebox.showerror("Couldn't clip", "Invalid time stamps.\nCould not clip file")
            elif m == "size_zero":
                messagebox.showerror("File size error", "Clipping size not specified\n")

        def file_type_clip(file_type, conversion_file, file_path, start, end):
            clip = conversion_file.subclip(start, end)
            try:
                if file_type == "video":
                    clip.write_videofile(file_path)
                else:
                    clip.write_audiofile(file_path)
            except Exception as e:
                print(e)
                return "error"

        if self.clip_file_path == '':
            cancel_message("no_file")
            return
        if clip_type == "size" and self._get_clipping_size() == 0:
            cancel_message("size_zero")
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
            file_n, file_ext = os.path.splitext(self.clip_file_path)
            file_name = ntpath.basename(file_n)
            file_type = self._check_extension(file_ext)
            if file_type == "video":
                conversion_file = VideoFileClip(self.clip_file_path)
            elif file_type == "audio":
                conversion_file = AudioFileClip(self.clip_file_path)
            try:
                is_range = False
                range_file_name = ''
                if clip_type == "number" or "size":
                    length = conversion_file.duration
                    sections = self._generate_sections(length, clip_type)
                    if sections == "error":
                        raise ClippingRangeError("Too many clippings")
                    else:
                        for index, (start, end) in enumerate(sections, start=1):
                            if self.clipping_event.is_set():
                                clip_name = f"part{index} - {file_name}{file_ext}"
                                file_path = ntpath.join(self.file_save_directory, clip_name)
                                response = file_type_clip(file_type, conversion_file, file_path, start, end)
                                self.num_clipped += 1
                                self.clipped_files.append(clip_name)
                                self._render_file_names(clipping=True)
                            else:
                                break
                elif clip_type == "range":
                    is_range = True
                    file_id = math.ceil(time.time())  # use time to give video id
                    clip_name = f"{file_ext}_{file_id} - {file_name}{file_ext}"
                    range_file_name = clip_name
                    file_path = ntpath.join(self.file_save_directory, clip_name)
                    start, end = self._get_clip_range()
                    response = file_type_clip(file_type, conversion_file, file_path, start, end)
                    if response == "error":
                        os.remove(path=file_path)  # delete error file
                        raise ClippingRangeError("Invalid range")
                self._end_of_clipping(range_clip=is_range, range_clip_file=range_file_name)
            except ClippingRangeError as e:
                if e == "Invalid range":
                    cancel_message("invalid_range")
                self.clipping_event.clear()
                self._clipping_check()
                return

        t = Thread(
            target=clipping_thread,
            name=f"Clipping thread"
        )
        t.setDaemon(True)
        print(f"{t.name} has started ...")
        t.start()

    def _get_file_details(self):
        file_n, file_ext = os.path.splitext(self.clip_file_path)
        file_name = ntpath.basename(file_n)
        file_type = self._check_extension(file_ext)
        if file_type == "video":
            conversion_file = VideoFileClip(self.clip_file_path)
        elif file_type == "audio":
            conversion_file = AudioFileClip(self.clip_file_path)
        self.file_length = conversion_file.duration
        self.formatted_file_length = str(datetime.timedelta(seconds=math.floor(self.file_length)))

    def _get_clip_range(self):
        start = self._get_seconds(self.start_hour_entry, self.start_min_entry, self.start_sec_entry)
        end = self._get_seconds(self.end_hour_entry, self.end_min_entry, self.end_sec_entry)
        return (start, end)

    def _get_seconds(self, hr, min, sec):
        hr = int(hr.get()) * 3600 if hr.get() != "" else 0
        min = int(min.get()) * 60 if min.get() != "" else 0
        sec = int(sec.get()) if sec.get() != "" else 0
        secs = hr + min + sec
        return secs

    def _clipping_check(self):
        """disable buttons while clipping is ongoing"""
        if self.clipping_event.is_set():
            self.select_audio_files_btn.configure(state=tkinter.DISABLED)
            self.select_video_files_btn.configure(state=tkinter.DISABLED)
            for i in self.clipping_btns_list:
                btn = i["btn"]
                if btn == self.action_btn:
                    pass
                else:
                    btn.configure(state=tkinter.DISABLED)
                btn
            self.action_btn.configure(
                text="Stop Clipping", command=lambda: self._manage_btns("stop_clipping")
            )
        else:
            self.select_audio_files_btn.configure(state=tkinter.NORMAL)
            self.select_video_files_btn.configure(state=tkinter.NORMAL)
            for i in self.clipping_btns_list:
                btn = i["btn"]
                if btn != self.action_btn:
                    btn.configure(state=tkinter.NORMAL)
            self.action_btn.configure(
                text=i["text"], command=lambda: self._manage_btns(i["command"])
            )

    def _end_of_clipping(self, error="", range_clip=False, range_clip_file=""):
        if range_clip:
            messagebox.showinfo("Clipping complete", f"All Done.\nFile_name={range_clip_file}")
        else:
            feedback = f"Completed files:{self.num_clipped}/{self.total_clips}"
            if self.clipping_cancelled:
                messagebox.showerror(
                    "Clipping canceled", f"Clipping canceled.\n\n{feedback}"
                )
            else:
                messagebox.showinfo("Clipping complete", f"All Done.\n\n{feedback}")
        self.clipping_event.clear()
        self._clipping_check()
        self._render_file_names(completed=True, range_clip=range_clip, range_clip_file=range_clip_file)
        print("Clipping complete")
        self._reset_vars()

        if error == "clipping_range":
            pass

    def _check_extension(self, file_ext):
        if file_ext[1:].upper() in self.acceptable_audio_file_list:
            return "audio"
        else:
            return "video"

    def _get_clipping_size(self):
        return self._get_seconds(self.size_of_clips_hr_entry, self.size_of_clips_min_entry,
                                 self.size_of_clips_sec_entry)

    def _generate_sections(self, len, clip_type):
        if clip_type == "size":
            clip_size_in_seconds = self._get_clipping_size()
            self.total_clips = math.ceil(len / clip_size_in_seconds)
            if self.total_clips > 20:
                messagebox.showerror(title="Too small clipping", message="The file generates too many clips")
                return "error"
            else:
                individual_clip = clip_size_in_seconds
        elif clip_type == "number":
            self.total_clips = int(self.num_clips.get())
            individual_clip = math.ceil(len / self.total_clips)
        sections = []
        for i in range(self.total_clips):
            if i == 0:
                start = 0
            else:
                start = i * individual_clip + 1
            if i < self.total_clips - 1:
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
        self.total_clips = 0
        self.file_length = 0
        self.formatted_file_length = 0
        self.num_clips.set(2)
        self.action_btn = None

    def _render_file_names(self, clipping=False, completed=False, file_select=False, range_clip=False,
                           range_clip_file=""):
        intro_text = f"Selected file:{self.clip_file_path}\n\nSave location:    {self.file_save_directory}\nFile Length:    {self.formatted_file_length}\n"
        text = ""
        title = intro_text + f"Number of clips:  {self.total_clips}\n\nClipped files:  {self.num_clipped}/{self.total_clips}\n\n"
        reverse_list = self.clipped_files[::-1]
        if clipping:
            v = ""
            for i in reverse_list:
                v += f"✓    {i}\n"
            text = f"{title}{v}"
        elif completed:
            if not range_clip:
                msg = "Clipping complete\n\n"
                if self.clipping_cancelled:
                    msg = "Clipping cancelled\n\n"
                v = ''
                for i in reverse_list:
                    v += f"      • {i}\n"
                text = title + msg + v
            else:
                text = f"Selected file:{self.clip_file_path}\n\nSave location:    {self.file_save_directory}\n\n      • {range_clip_file} clipped"
        elif file_select:
            text = intro_text
        else:
            text = "YOUR CLIPPED FILES WILL APPEAR HERE"

        self.files_textbox.config(state="normal")
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, text)
        self.files_textbox.config(wrap=WORD, state="disabled")
