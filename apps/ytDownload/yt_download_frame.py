from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter
from tkinter import OptionMenu
from customtkinter import CTkButton, CTkLabel, CTk,CTkEntry,CTkOptionMenu

from pytube import YouTube
import pytube.exceptions as pytExcept
from pytube import Playlist
from math import ceil
import threading



from constants import Constants
from apps.converter.windows import DWindow, folder_select


class error_messages:
    invalid ="Invalid url. Confirm and try again",
    empty= "No url provided. Try again"
    notPlaylist = "Link provided is not a playlist"
    playlistInvalid = 'Playlist link is not valid.'
class YtDownloaderFrame(Frame):

    def __init__(self,root):
        super().__init__(root)


        self.video_qualities = ["highest",'2160p','1440p','1080p','720p','480p','360p','240p']
        self.download_playlist = []
        self.download_quality = StringVar()
        self.download_quality.set("highest")
        self.save_directory =''





        self.root = root
        self.root.title("YT_Download | VIDMAN")
        self.main_label = CTkLabel(
            self, text="Welcome", text_font=("Montserrat", 30, "bold"))
        self.main_label.pack()

        self.link_label = CTkLabel(self,text=f"Enter the youtube link here",text_font=("Montserrat", 15), wraplength=900)
        self.link_label.pack()

        self.link_entry = CTkEntry(self)
        self.link_entry.pack(fill="both", pady=10)

        # self.video_quality = OptionMenu(self,self.sel_quality,*self.video_qualities)
        self.video_quality = CTkOptionMenu(self,variable=self.download_quality,values=self.video_qualities)
        self.video_quality.pack(pady=10)

        self.downloadBtn = CTkButton(self, text="Download playlist", fg_color=Constants.grey,
                                          command= self._download_videos)
        self.downloadBtn.pack()

        self.scroll_frame = Frame(self)
        self.scroll_frame.pack(pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.scroll_frame, height=15, bg=Constants.grey,
                                                       font=("Montserrat", 10))
        self.files_textbox.pack(fill="both")


    def _download_videos (self):
        #TODO: add functionality for playlist or video availability/privacy check
        try:
            url = self.link_entry.get()
            desc = YouTube(url).description
            self.save_directory = filedialog.askdirectory()
            self._downloadAction([url], 0)
        except pytExcept.RegexMatchError:
            self.download_playlist = Playlist(url)
            self._playlistDownload()      
            #self.download_playlist.length ##use to generate error in case of non-playlist url
        except Exception as e:
            #TODO: add privacy/availability check
            if self.link_entry.get() == "":
                messagebox.showerror("Missing url", error_messages.empty)
            else:
                messagebox.showerror("Incorrect url", error_messages.invalid)
            return


    def _playlistDownload(self):
        #TODO: add functionality to skip private/unavailable videos in playlist  
        links =[]      
        try:
            for url in self.download_playlist:
                links.append(url)
        except:
            messagebox.showerror("Incorrect url", error_messages.playlistInvalid)
            return

        self.save_directory = filedialog.askdirectory()
        #TODO: sort out this for threading
        size = ceil(len(links)/4) # size of each of the list for the threads
        def split_link(links,size):
            for i in range(0,len(links),size):                
                yield links[i:i+size]

        link = list(split_link(links,size))
        self._downloadThreading(link=link)

    def _downloadAction(self, linkList, threadNum):
        quality = self.download_quality.get()
        for i in linkList:
            yt = YouTube(i)
            # print(yt.check_availability())
            if quality =="highest":
                ys = yt.streams.get_highest_resolution()
            else:
                ys = yt.streams.get_by_resolution(quality)
            print(ys.title)
            # filename = ys.download(output_path=self.save_directory ,max_retries=1)
            # print(f"threading {threadNum} -->  {filename.split('/')[-1]} Downloaded")

    def _downloadThreading(self,link):
        #TODO: Modify thread functionality depending on playlist size
        #TODO: add index error catch for threads
        downloaders = [self._downloadAction(link[x],y) for x,y in enumerate(range(1,5))]
        threads = [threading.Thread(target=downloader, name=f"d{index}") for index,downloader in enumerate(downloaders,start=1)]
        for thread in threads:
            thread.start()

        # downloader = self._downloadAction(link[0],1)
        # thread = threading.Thread(target=downloader, name=f"d1")
        # thread.start()


    def _cancel_conversion(self):
        return messagebox.askokcancel("Stop Downloads", "Cancel ongoing downloads?")

    def _render_file_names(self, list_to_render, downloading=False, final=False, completed=True):
        """renders page content to bottom text box"""
        tag_font = ("Montserrat", 10, "bold")
        text = ""
    def reset_vars (self):
        "resets variables"
        self.download_playlist =[]
        self.video_quality.set("highest")

        


