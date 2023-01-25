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
from apps.ytDownload.functions import split_link, generate_filename, generate_details


class error_messages:
    invalid = "Invalid url. Confirm and try again",
    empty = "No url provided. Try again"
    notPlaylist = "Link provided is not a playlist"
    playlistInvalid = 'Playlist link is not valid.'


class EmptyUrl(Exception):
    pass


class SingleVideoPlaylistError(Exception):
    pass


class YtDownloaderFrame(Frame):

    def __init__(self, root):
        super().__init__(root)

        # CONSTANTS
        self.threadCount = 3

        self.video_qualities = ["highest", '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p']
        self.download_playlist = []
        self.download_quality = StringVar()
        self.save_directory = ''
        self.links_break = []
        self.single_video_object = None
        self.skipped = 0
        self.failed_video_list = []
        self.downloading_list = []
        self.completed_video_list = []
        self.download_details = ''
        self.download_cancelled = False
        self.is_playlist = False
        self.number_files = False

        # AUDIOS
        self.audio_list = []
        self.completed_audio_list = []
        self.failed_audio_list = []

        # Thread management
        self.threads = []
        self.video_event = Event()
        self.audio_event = Event()
        # self.video_event.set()



        #***********FRAME BODY************/
        self.root = root
        self.main_label = CTkLabel(
            self, text="Welcome", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)

        self.link_label = CTkLabel(self, text=f"Enter the youtube link here", text_font=("Montserrat", 15),
                                   wraplength=900)
        self.link_label.grid(row=1, column=0, columnspan=2)

        self.link_entry = CTkEntry(self)
        self.link_entry.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")

        self.video_quality = CTkOptionMenu(self, variable=self.download_quality, values=self.video_qualities)
        self.video_quality.grid(row=3, column=0, columnspan=2, pady=10)

        self.download_video_btn = CTkButton(self, text="Download video(s)", fg_color=Constants.grey,
                                            command=lambda: self._manage_btns('start_video_download'))

        self.download_video_btn.grid(row=4, column=0, pady=(0, 10))

        self.download_audio_btn = CTkButton(self, text="Download audio(s)", fg_color=Constants.grey,
                                            command=lambda: self._manage_btns('start_audio_download'))

        self.download_audio_btn.grid(row=4, column=1)

        self.clear_btn = CTkButton(self, text="Clear",
                                   command=lambda: self._manage_btns(btn="clear_url_entry"),
                                   fg_color=Constants.grey)
        self.clear_btn.grid(row=5, column=0, columnspan=2)

        self.scroll_frame = Frame(self)
        self.scroll_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.scroll_frame, height=15, bg=Constants.grey,
                                                       font=("Montserrat", 10))
        self.files_textbox.pack(fill="both")
        self._reset_vars()
        self._render_file_names(intro=True)

    def _manage_btns(self, btn):
        if btn in ("start_video_download", "start_audio_download"):
            self.clear_btn.configure(text="Cancel download",
                                     command=lambda: self._manage_btns("end_downloads"))
        # if False in (self.video_event.is_set(),self.audio_event.is_set()):
        #     self._end_of_downloads()    
        if btn == "clear_url_entry":
            self.link_entry.delete(0, END)
        elif btn == 'start_video_download':
            self.video_event.set()
            self._download_videos()
            # self._end_of_downloads()

        elif btn == "end_downloads":
            self.video_event.clear()
            self.audio_event.clear()
            self.clear_btn.configure(text="Clear",
                                     command=lambda: self._manage_btns("clear_url_entry"))
        elif btn == "start_audio_download":
            self.audio_event.set()
            self.downloadAudio()
            # self._end_of_downloads()
        self._downloading_check()

    def _check_url(self, url):
        if self.link_entry.get() == "":
            messagebox.showerror("Missing url", error_messages.empty)
        try:
            self.single_video_object = YouTube(url)
        except pytExcept.RegexMatchError:
            self.download_playlist = Playlist(url)
            self.is_playlist = True

        except Exception as e:
            print(e)
            messagebox.showerror("Incorrect url", error_messages.invalid)
            return
        self.save_directory = filedialog.askdirectory().replace("/",
                                                                "\\")  # convert path to raw string for to avoid OSError: [Errno 22] Invalid argument
        if self.is_playlist:
            time.sleep(0.5)
            self.number_files = messagebox.askyesno("Numbering prompt",
                                                    "Do you want to number files according to the playlist order?",
                                                    default="no")

    def _download_videos(self):
        # TODO: add functionality for playlist or video availability/privacy check
        # TODO: add functionality for single video download
        url = self.link_entry.get()
        self._check_url(url=url)
        singleVid = False
        self._playlistDownload(singleVideo=singleVid, singleLink=url)

    def _playlistDownload(self, singleLink, singleVideo=False):
        # TODO: add functionality to skip private/unavailable videos in playlist
        self._render_file_names(intro=True)  # clear textbox
        links = []
        if self.is_playlist:
            for url in self.download_playlist.video_urls:
                links.append(url)
        else:
            links = [singleLink]

        self.links_break = split_link(self._enumerate_linklist(links), self.threadCount)
        self._downloadThreading()
    def _enumerate_linklist(self,links):
        """returns enumerated links for eventual file numbering on playlist download"""
        return [[videoNum, link] for videoNum, link in
                enumerate(links, start=1)] 
    def downloadAudio(self):
        def singleAudio(get_url,index="null"):
            file = YouTube(url=get_url)
            title = f"{generate_filename(yt_obj=file, idx=index, is_playlist=self.is_playlist, numbering=self.number_files)}.mp3" 
            try:
                file.streams.get_audio_only().download(output_path=self.save_directory, filename=title,
                                                       skip_existing=True)
                self.completed_audio_list.append(title)
                self.audio_list.append(f"{title}")
                self._render_file_names(audio_download=True)
                print(f"{title} downloaded")
            except Exception as e:
                print(e)
                self.audio_list.append(f"X {title}")
                self.failed_audio_list.append(title)
                print(f"{title} failed")
                pass
            self.update_idletasks()

        def audio_downloading_func(get_url):
            if self.is_playlist:
                for idx ,link in enumerate(self.download_playlist,start=1):
                    if self.audio_event.is_set():
                        singleAudio(link,index=idx)
                    else:
                        self.download_cancelled = True
                        break
            else:
                singleAudio(get_url)
            self._render_file_names(audio_finished=True, )

        url = self.link_entry.get()
        self._check_url(url=url)
        def func():
            self._downloading_check()
            try:
                audio_downloading_func(get_url=url)
            except Exception as e:
                print(e)
                pass
        t = threading.Thread(target=func, daemon=True, name="Audio Thread")
        print(f"audio download(s) has started")
        func()
        self._end_of_downloads(is_audio=True)



    def _download_video_thread(self, linkList, threadNum):
        quality = self.download_quality.get()
        print(f"Thread {threadNum} started :{len(linkList)} files")

        # using enumerate list to generate numbered file names in event of unnumbered file name or file numbering done at end of file name
        # to aid in file sorting in directory 
        def singleDownload(index):
            yt = YouTube(url)
            try:
                filename = f"{generate_filename(yt_obj=yt, idx=index, is_playlist=self.is_playlist, numbering=self.number_files)}.mp4"
                stream = yt.streams
                try:
                    stream.get_by_resolution(str(quality)).download(output_path=self.save_directory, max_retries=1)
                except Exception as e:
                    if self.is_playlist:  # avoid rename of single video files
                        stream.get_highest_resolution().download(output_path=self.save_directory, filename=filename,
                                                                 max_retries=1, skip_existing=True)
                    else:
                        stream.get_highest_resolution().download(output_path=self.save_directory, max_retries=1,
                                                                 skip_existing=True)
                print(f" Thread {threadNum} -->{filename} downloaded")
                self.downloading_list.append(f"✓ {filename}")
                self.completed_video_list.append(filename)
            except (pytExcept.PytubeError, AttributeError) as e:
                self.skipped += 1
                # self.skipped_video_url.append([index,url])
                self.failed_video_list.append(url)
                self.downloading_list.append(f"× {url}")
                print(f"Thread {threadNum} --> {url} not downloaded")
            self._render_file_names(downloading=True)
            self.root.update_idletasks()

        for index, url in linkList:
            if self.video_event.is_set():
                singleDownload(index=index)
            else:
                self.download_cancelled = True
                break

    def _end_of_downloads(self,is_audio=False):

        feedback = "Cancelled" if self.download_cancelled else "done"
        if self.download_cancelled:
            messagebox.showerror(
                "Downloads canceled", f"Conversion canceled.\n{feedback}")
            self._render_file_names(cancelled=self.download_cancelled,audio_finished=is_audio)

        else:
            messagebox.showinfo("Downloads complete",
                                f"All Done.\n{feedback}")
            self._render_file_names(final=True,audio_finished=is_audio)
        self._downloading_check()
        self._reset_vars()

    def _downloadThreading(self):
        """runs the threads for video downloads"""
        self.download_details = generate_details(self.is_playlist, self.download_playlist, self.single_video_object)
        num_of_downloaders = len(self.links_break)
        print(self.download_details)
        print(f"Total threads : {num_of_downloaders}\n")

        threads = []
        for x in range(num_of_downloaders):
            t = threading.Thread(target=self._download_video_thread, daemon=True, name=f"Thread {x + 1}",
                                 args=(self.links_break[x], (x + 1)))
            threads.append(t)
            t.start()
        # TODO: add thread join method
        for thread in threads:
            thread.join()
        # async def main():
        #     list_of_tasks = []
        #     for x in range(num_of_downloaders):
        #         task = asyncio.create_task(self._downloadAction(self.links_break[x], x + 1))
        #         list_of_tasks.append(task)              
        #         print(f"started async {x + 1}")
        #     for task in list_of_tasks:
        #         await task

        # asyncio.run(main())
        

    def _downloading_check(self):
        """disable buttons while download is ongoing"""
        if self.video_event.isSet() or self.audio_event.isSet():
            self.download_audio_btn.configure(state=tkinter.DISABLED)
            self.download_video_btn.configure(state=tkinter.DISABLED)
        else:
            self.download_audio_btn.configure(state=tkinter.NORMAL)
            self.download_video_btn.configure(state=tkinter.NORMAL)

    def _main_thread(self):
        download_thread = Thread(target=self._downloadThreading, name="Main thread")
        download_thread.setDaemon(True)
        download_thread.start()
        print(f'{download_thread.name} has started')
        download_thread.join()
        self._end_of_downloads()
        print(f"{download_thread.name} finished")
        # self._render_file_names(final=True)
        # self._reset_vars()

    def _cancel_conversion(self):
        return messagebox.askokcancel("Stop Downloads", "Cancel ongoing downloads?")

    def _render_file_names(self, downloading=False, final=False, intro=False, cancelled=False, render_list=[],
                           **kwargs):
        """renders page content to bottom text box"""
        # TODO: add skipped files display
        # TODO: add file name rendering and progress to the Textbox at bottom similar to converter app
        tag_font = ("Montserrat", 10, "bold")
        text = ""

        reverse_download_list = self.completed_video_list[::-1]
        reverse_downloading_list = self.downloading_list[::-1]
        reverse_audio_list = self.audio_list[::-1]

        if downloading:
            v = ""
            for i in reverse_downloading_list:
                v += f"   {i}\n"
            text = f'{self.download_details}\n\n{v}'
        elif kwargs.get('audio_download'):
            text = "DOWNLOADED AUDIO FILES\n\n"
            for i in reverse_audio_list:
                text += f"        {i}\n"
        else:
            if intro:
                text = "SELECTED FILES WILL BE DISPLAYED HERE"
            else:
                not_downloaded = "FAILED URLS\n\n"
                if self.failed_video_list:
                    for index, url in self.failed_video_list:
                        not_downloaded += f"•   FileNum: {index} url:{url}\n"
                else:
                    not_downloaded += "•    No downloads failed"

                downloaded = "DOWNLOADED FILES\n\n"
                if reverse_download_list:
                    for i in self.completed_video_list:
                        downloaded += f"    {i}\n"
                else:
                    downloaded += "•    No files Downloaded"

                def final_text(status, completed_list, failed_list, video=True):
                    downloaded = "DOWNLOADED VIDEO FILES\n\n" if video else "DOWNLOADED AUDIO FILES\n\n"
                    not_downloaded = "FAILED VIDEO URLS\n\n" if video else "FAILED AUDIO DOWNLOADS\n\n"
                    if completed_list:
                        for i in completed_list[::-1]:
                            downloaded += f"•    {i}\n"
                    else:
                        downloaded += "•    No files Downloaded"
                    if failed_list:
                        for i in failed_list:
                            not_downloaded += f"•    {i}\n"
                    else:
                        not_downloaded += "•    No downloads failed"
                    attachment = f"{not_downloaded}\n\n{downloaded}"

                    return f'SESSION {(status).capitalize()}\n\n{attachment}'


                if kwargs.get('audio_finished'):
                    if not self.download_cancelled:
                        text = final_text("complete", self.completed_audio_list, self.failed_audio_list, False)
                    else:
                        text = final_text("cancelled", self.completed_audio_list, self.failed_audio_list, False)
                else:
                    if final:
                        text = final_text("COMPLETE", self.completed_video_list, self.failed_video_list)
                    elif cancelled:
                        text = final_text("CANCELLED", self.completed_video_list, self.failed_video_list)


        self.files_textbox.config(state="normal")
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, text)
        self.files_textbox.config(wrap=WORD, state="disabled")

    def _reset_vars(self):
        "resets variables"
        self.download_playlist = []
        self.video_quality.set("480p")
        self.links_break = []
        self.single_video_object = None
        self.skipped = 0
        self.downloading_list = []
        self.completed_video_list = []
        self.failed_video_list = []
        self.download_details = ''
        self.download_cancelled = False
        self.is_playlist = False
        self.number_files = False

        self.failed_audio_list = []
        self.completed_audio_list = []
        self.audio_list = []
