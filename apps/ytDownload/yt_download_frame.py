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
        self.download_quality.set("720p")
        self.save_directory =''
        self.links_break = []
        self.singleVidUrl=''





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
        #TODO: add functionality for single video download
        url = self.link_entry.get()
        singleVid = False
        class SingleVideoPlaylistError(Exception):
            pass
        try:
            if YouTube(url):
                raise SingleVideoPlaylistError
            self.download_playlist = Playlist(url)
        except SingleVideoPlaylistError: 
            singleVid = True
            self.singleVid = YouTube(url)
            pass  
        except Exception:
            #TODO: add privacy/availability check
            if self.link_entry.get() == "":
                messagebox.showerror("Missing url", error_messages.empty)
            else:
                messagebox.showerror("Incorrect url", error_messages.invalid)
            return

        self._playlistDownload(singleVideo=singleVid,singleLink=url)

    def _playlistDownload(self,singleLink,singleVideo=False):
        #TODO: add functionality to skip private/unavailable videos in playlist  
        links =[]
        if not singleVideo:     
            try:
                for url in self.download_playlist.video_urls:
                    links.append(url)
            except:
                messagebox.showerror("Incorrect url", error_messages.playlistInvalid)
                return
        else:
            links = [singleLink]

        self.save_directory = filedialog.askdirectory()
        enumerate_Linklist = [[videoNum,link] for videoNum,link in enumerate(links,start=1)] # enumerate for eventual file numbering on playlist download
        size = ceil(len(links)/4) # get size of each of the lists for the threading
        def split_link(links,size):
            for i in range(0,len(links),size):                
                yield links[i:i+size]


        # self.links_break = list(split_link(links,size))
        #USING enumerate numbering
        self.links_break = list(split_link(enumerate_Linklist,size))
        self._downloadThreading(num_of_links=len(links))

    def _downloadAction(self, linkList, threadNum):
        quality = self.download_quality.get()
        # using enumerate list to generate numbered file names in event of unnumbered file name or file numbering done at end of file name
        # to aid in file sorting in directory 
        for index,url in linkList:
            yt = YouTube(url)
            if quality =="highest":
                ys = yt.streams.get_highest_resolution()
            else:
                ys = yt.streams.get_by_resolution(quality)            
            filename = yt.title
            if len(linkList)>1:
                try:
                    int(filename.split(".")[0])
                except ValueError:
                    filename= f"{index}.{filename}"
            # ys.download(output_path=self.save_directory,filename=filename,max_retries=1)
            print(f"Thread{threadNum} \n-->{filename} downloaded")

    def _downloadThreading(self,num_of_links):
        #TODO: Modify thread functionality depending on playlist size
        #TODO: add index error catch for threads
        download_details = f"Video Title : {self.singleVid.title}\nChannel : {self.singleVid.author}\nVideo views: {self.singleVid.views}\n\n" if num_of_links ==1 else "Playlist Name : {}\nChannel Name  : {}\nTotal Videos  : {}\nTotal Views   : {}\n".format(self.download_playlist.title,self.download_playlist.owner,self.download_playlist.length,self.download_playlist.views)
        if num_of_links<4:
            num_of_downloaders = 1            
        else:
            num_of_downloaders = 4

        downloaders = [self._downloadAction(self.links_break[x],y) for x,y in enumerate(range(1,num_of_downloaders+1))]
        threads = [threading.Thread(target=downloader, name=f"d{index}") for index,downloader in enumerate(downloaders,start=1)]
        print(download_details) 
        print(f"Total threads:{len(threads)}\n")
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()#waits for all threads to finish
        print("Downloads complete")

    def _cancel_conversion(self):
        return messagebox.askokcancel("Stop Downloads", "Cancel ongoing downloads?")

    def _render_file_names(self, list_to_render, downloading=False, final=False, completed=True):
        """renders page content to bottom text box"""
        #TODO: add skipped files display
        #TODO: add file name rendering and progress to the Textbox at bottom similar to converter app
        tag_font = ("Montserrat", 10, "bold")
        text = ""
    def reset_vars (self):
        "resets variables"
        self.download_playlist =[]
        self.video_quality.set("highest")
        self.links_break =[]
        self.singleVidUrl=''

        


