from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox, WORD, StringVar,Label
import tkinter
from tkinter import OptionMenu
from customtkinter import CTkButton, CTkLabel, CTk,CTkEntry,CTkOptionMenu

from pytube import YouTube
import pytube.exceptions as pytExcept
from pytube import Playlist
from math import ceil
from threading import Thread, Event
import threading
from concurrent.futures import  ThreadPoolExecutor,Executor
from multiprocessing.pool import ThreadPool,Pool



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

        #CONSTANTS
        self.threadCount = 4


        self.video_qualities = ["highest",'2160p','1440p','1080p','720p','480p','360p','240p']
        self.download_playlist = []
        self.download_quality = StringVar()
        self.save_directory =''
        self.links_break = []
        self.singleVidUrl=''
        self.skipped=0
        self.skipped_list=[]
        self.skipped_urls=[]
        self.downloading_list=[]
        self.downloaded_list=[]
        self.download_details =''
        self.num_of_links =0
        self.download_cancelled = False

        # Thread management
        self.threads = []
        self.event = Event()
        # self.event.set()





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
                                          command=lambda: self._manage_btns('start_download'))

        self.downloadBtn.pack(pady=(0,10))

        self.clear_btn = CTkButton(self, text="Clear",
                                   command=lambda: self._manage_btns(btn="clear_url_entry"),
                                   fg_color=Constants.grey)
        self.clear_btn.pack()           

        self.scroll_frame = Frame(self)
        self.scroll_frame.pack(pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.scroll_frame, height=15, bg=Constants.grey,
                                                       font=("Montserrat", 10))
        self.files_textbox.pack(fill="both")
        self._reset_vars()
        self._render_file_names(intro=True)


    def _manage_btns(self,btn):
        if btn =="clear_url_entry":
            self.link_entry.delete(0, END)
        elif btn == 'start_download':
            self.event.set()
            self.clear_btn.configure(text="Cancel download",
                command=lambda: self._manage_btns("end_downloads")) 
            self._download_videos()     

        elif btn=="end_downloads":
            self.event.clear()
            self.clear_btn.configure(text="Clear",
                command=lambda: self._manage_btns("clear_url_entry"))

    def _download_videos (self):
        #TODO: add functionality for playlist or video availability/privacy check
        #TODO: add functionality for single video download
        url = self.link_entry.get()
        singleVid = False
        class SingleVideoPlaylistError(Exception):
            pass
        try:
            try:
                if YouTube(url):
                    raise SingleVideoPlaylistError
            except pytExcept.RegexMatchError:                              
                self.download_playlist = Playlist(url)
        except (SingleVideoPlaylistError) :
            singleVid = True
            self.singleVid = YouTube(url)
        except Exception as e:
            #TODO: add privacy/availability check
            print(e)
            if self.link_entry.get() == "":
                messagebox.showerror("Missing url", error_messages.empty)
            else:
                messagebox.showerror("Incorrect url", error_messages.invalid)
            return
        finally:
            self._playlistDownload(singleVideo=singleVid,singleLink=url)

    def _playlistDownload(self,singleLink,singleVideo=False):
        #TODO: add functionality to skip private/unavailable videos in playlist  
        self._render_file_names(intro=True) # clear textbox
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

        self.save_directory = filedialog.askdirectory().replace("/", "\\") # convert path to raw string for to avoid OSError: [Errno 22] Invalid argument
        enumerate_Linklist = [[videoNum,link] for videoNum,link in enumerate(links,start=1)] # enumerate for eventual file numbering on playlist download
        self.num_of_links=len(links)
        size = ceil(len(links)/self.threadCount) # get size of each of the lists for the threading
        def split_link(links,size):
            """splits links for threading"""
            if self.num_of_links >=self.threadCount:
                for i in range(0,len(links),size):                
                    yield links[i:i+size]
            else:
                yield links

        #USING enumerate numbering
        self.links_break = list(split_link(enumerate_Linklist,size)) 
        self._downloadThreading()

    def _generate_filename(self,yt_obj,idx):
        f_name = yt_obj.title
        if self.num_of_links > 1:
            try:
                int(f_name.split(".")[0])
            except ValueError:
                f_name = f"{idx}. {f_name}"
        else:
            # return unicodedata.normalize("NFKD",f_name) # to preserve filename structure  (normal form for the Unicode string unistr)
            f_name = r"%s" %f_name
        return f_name
        
    def _downloadAction(self, linkList, threadNum):
        quality = self.download_quality.get()
        # using enumerate list to generate numbered file names in event of unnumbered file name or file numbering done at end of file name
        # to aid in file sorting in directory 
        def singleDownload():
            yt = YouTube(url)
            try:
                stream = yt.streams
                filename = f"{self._generate_filename(yt,index)}.mp4"
                try: 
                    stream.get_by_resolution(str(quality)).download(output_path=self.save_directory,max_retries=1)
                except Exception as e:
                    print(f"Try 1:{e}")
                    if self.num_of_links > 1: # avoid rename of single video files
                        stream.get_highest_resolution().download(output_path=self.save_directory,filename=filename ,max_retries=1)                           
                    else:
                        stream.get_highest_resolution().download(output_path=self.save_directory,max_retries=1)                           
                print(f" Thread {threadNum} -->{filename} downloaded")
                self.downloading_list.append(f"✓ {filename}")
                self.downloaded_list.append(filename)
            except (pytExcept.PytubeError,AttributeError) as e:
                print(f"Try 2:{e}")
                self.skipped +=1
                self.skipped_urls.append([index,url])
                self.downloading_list.append(f"× {url}")
                print(f"Thread {threadNum} --> {url} not downloaded")
            self._render_file_names(downloading=True)
            self.root.update_idletasks()

        for index,url in linkList:
            if self.event.is_set():singleDownload()
            else:
                self.download_cancelled = True
                break
        

    def end_of_downloads(self):
        feedback = "Cancelled" if self.download_cancelled else "done" 
        if self.download_cancelled:
            messagebox.showerror(
                "Downloads canceled", f"Conversion canceled.\n{feedback}")
            self._render_file_names(cancelled=self.download_cancelled)

        else:
            messagebox.showinfo("Downloads complete",
                                f"All Done.\n{feedback}")
            self._render_file_names(final=True)              
        

    def _downloadThreading(self):
        """runs the threads for video downloads"""
        #TODO: Modify thread functionality depending on playlist size
        #TODO: add index error catch for threads
        self.download_details = f"Video Title : {self.singleVid.title}\nChannel : {self.singleVid.author}\nVideo views: {self.singleVid.views}" if self.num_of_links ==1 else "Playlist Name : {}\nChannel Name  : {}\nTotal Videos  : {}\nTotal Views   : {}".format(self.download_playlist.title,self.download_playlist.owner,self.download_playlist.length,self.download_playlist.views)
        num_of_downloaders = self.threadCount if self.num_of_links >= self.threadCount else 1
        # downloaders = [self._downloadAction(self.links_break[x],y) for x,y in enumerate(range(1,num_of_downloaders+1))]
        print(self.download_details) 
        print(f"Total threads : {num_of_downloaders}\n")
        threads = [threading.Thread(target=self._downloadAction,daemon=True, name=f"Thread {x+1}",args=(self.links_break[x],(x+1))) for x in range(num_of_downloaders)]
        [(t.start(),print(f'{t.name} has started')) for t in threads]  # start all threads
        #TODO: add thread join method
        # m_list = tuple((self.links_break[x],y) for x,y in enumerate(range(1,num_of_downloaders+1)))
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #     # executor.map(self._downloadAction, *zip(*m_list))
        #     executor.map(self._downloadAction, *zip((self.links_break[0],1),(self.links_break[0],1)))

        # print("finished")

        # self.end_of_downloads()


    def downloading(self):
        self.clear_btn.configure(state=tkinter.DISABLED, text="Clear Selection",command=lambda: self._manage_btn("clear_selection"))

    def _main_thread(self):
        download_thread = Thread(target=self._downloadThreading, name="Main thread")
        download_thread.setDaemon(True)
        download_thread.start()
        print(f'{download_thread.name} has started')
        download_thread.join()
        print(f"{download_thread.name} finished")
        self._render_file_names(final=True)
        self._reset_vars()

    def _cancel_conversion(self):
        return messagebox.askokcancel("Stop Downloads", "Cancel ongoing downloads?")

    def _render_file_names(self, downloading=False, final=False, intro=False,cancelled=False):
        """renders page content to bottom text box"""
        #TODO: add skipped files display
        #TODO: add file name rendering and progress to the Textbox at bottom similar to converter app
        tag_font = ("Montserrat", 10, "bold")
        text = ""

        reverse_download_list = self.downloaded_list[::-1]
        reverse_downloading_list = self.downloading_list[::-1]
              
        if downloading:
            v=""
            for i in reverse_downloading_list:
                v+=f"   {i}\n"
            text = f'{self.download_details}\n\n{v}'
        else:
            if intro:
                text = "SELECTED FILES WILL BE DISPLAYED HERE"
            else:
                not_downloaded ="FAILED URLS\n\n"
                if self.skipped_urls:
                    for index,url in self.skipped_urls:
                        not_downloaded +=f"•   FileNum: {index} url:{url}\n"
                else:
                     not_downloaded+="•    No downloads failed"

                downloaded = "DOWNLOADED FILES\n\n"
                if reverse_download_list:                
                    for i in self.downloaded_list:
                        downloaded +=f"    {i}\n"
                else:downloaded += "•    No files Downloaded"

                def final_text(status):
                    return f'SESSION {(status).capitalize()}\n\n{not_downloaded}\n\n{downloaded}'

                if final:                
                    text = final_text("COMPLETE")
                elif cancelled:
                    text = final_text("CANCELLED")

        self.files_textbox.config(state="normal")
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, text)
        self.files_textbox.config(wrap=WORD, state="disabled")


    def _reset_vars (self):
        "resets variables"
        self.download_playlist =[]
        self.video_quality.set("480p")
        self.links_break =[]
        self.singleVidUrl=''
        self.skipped=0
        self.skipped_list=[]
        self.downloading_list=[]
        self.downloaded_list=[]
        self.skipped_urls=[]
        self.download_details =''
        self.num_of_links = 0
        self.download_cancelled = False


        


