#original repo from https://github.com/prokunal/Smart-Youtube-Playlist-Downloader/blob/main/README.md
# 
# run py3/py/python3 main.py "youtube_url" "quality_of_video"
#if quality not specified will download highest quality - use 480p,720p etc
# eg python3 .\smart.py "https://www.youtube.com/watch?v=vStJoetOxJg&list=PLkDaE6sCZn6FNC6YRfRQc_FbeQrF8BwGI" "480p"
#create venv and install
# pip install pytube3 pytube

from pytube import YouTube
from pytube import Playlist
from math import ceil
import sys
import threading

try:
    p = Playlist(sys.argv[1])
    video_quality = Playlist(sys.argv[2])
except IndexError:
    video_quality = "highest"
except:
    print('usage: python3 {} url'.format(__file__.split('/')[-1]))
    sys.exit(0)


#global links
print("Playlist Name : {}\nChannel Name  : {}\nTotal Videos  : {}\nTotal Views   : {}".format(p.title,p.owner,p.length,p.views))
links = []
size = 0

try:
    for url in p.video_urls:
        links.append(url)
except:
    print('Playlist link is not valid.')
    sys.exit(0)


size = ceil(len(links)/4)
def split_link(links,size):
    for i in range(0,len(links),size):
        yield links[i:i+size]

link = list(split_link(links,size))

print("Downloading Started...\n")
def downloader1():
    downloadAction(link[0],1)

def downloader2():
    downloadAction(link[1],2)

def downloader3():
    downloadAction(link[2],3)

def downloader4():
    downloadAction(link[3],4)

def downloadAction(linkList, threadNum):
    for i in linkList:
        yt = YouTube(i)
        if video_quality=="highest":
            ys = yt.streams.get_highest_resolution()
        else:
            ys = yt.streams.get_by_resolution(video_quality)

        print(ys.title)
        
        # filename = ys.download()
        # print(f"threading {threadNum} -->  {filename.split('/')[-1]} Downloaded")


##Threads
t1 = threading.Thread(target=downloader1, name='d1')
t2 = threading.Thread(target=downloader2,name='d2')
t3 = threading.Thread(target=downloader3, name='d3')
t4 = threading.Thread(target=downloader4,name='d4')
t1.start()
t2.start()
t3.start()
t4.start()