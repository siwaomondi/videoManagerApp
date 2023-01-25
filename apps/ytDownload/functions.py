import math


def split_link(links,threadCount):
    """split the links into th corresponding threads.
    retuns a list containing lists of the original passed link"""
    num_of_links = len(links)
    yield_result =[]
    if num_of_links >= threadCount:
        remainder = num_of_links % threadCount
        size = num_of_links/threadCount  # get approx size of each of the lists for the threading
        if remainder==0:
            size = int(size)
            for i in range(0, num_of_links, size):
                    yield_result.append(links[i:i + size])
        else:
            x = math.floor(size)
            y = threadCount*x
            for i in range(0, y,x):
                yield_result.append(links[i:i + x])
            yield_result[-1].extend(links[num_of_links-remainder:num_of_links])
                
    else:
        yield_result.append(links)

    return yield_result

def fetch_details(object, var):
    """error handler if pytube unable to fetch data    
    returns not found if error from pytube fetch"""
    try:
        return getattr(object, var)
    except:
        return "Not Found"
        
def generate_details(playlist:bool):
    """returns formatted string of the download process details"""
    if playlist:
        details = f"Playlist Name : {fetch_details(self.download_playlist, 'title')}\nChannel Name  : {fetch_details(self.download_playlist, 'owner')}\nTotal Videos  : {fetch_details(self.download_playlist, 'length')}\nTotal Views   : {fetch_details(self.download_playlist, 'views')}"
    else:
        details = f"Video Title : {fetch_details(self.singleVid, 'title')}\nChannel : {fetch_details(self.singleVid, 'author')}\nVideo views: {fetch_details(self.singleVid, 'views')}"
    return details

def generate_filename(yt_obj,is_playlist=False, idx="null"):
    """returns formatted raw filename """

    f_name = getattr(yt_obj, "title")

    f_name = f_name.replace("/",
                            "_")  # catch file naming from youtube to avoid clash with directory naming [Errno 2] error
    f_name = f_name.replace("\\", "_")
    if is_playlist and idx != "null":
        try:
            int(f_name.split(".")[0])
        except ValueError:
            f_name = f"{idx}. {f_name}"
    else:
        # to preserve filename structure  (normal form for the Unicode string unistr)
        f_name = r"%s" % f_name
    return f_name
