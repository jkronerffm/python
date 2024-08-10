import pafy
import vlc
import logging

def getYoutubeStreamUrl(url):
    youtubeStreamUrl = None
    try:
        logging.debug("call pafy.new(%s)" % url)
        video = pafy.new(url)
        logging.debug("video=%s, call video.getbestaudio()" % video)
        best = video.getbestaudio()
        if best != None:
            youtubeStreamUrl = best.url
        else:
            best = video.getbest()
            if best != None:
                youtubeStreamUrl = best.url
    except Exception as e:
        logging.error("exception (%s) occurred" % (str(e)))
    finally:
        return youtubeStreamUrl

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    youtubeId = "BFukVGpZL3o"#"hM32YSzZhbo"
    url = "https://www.youtube.com/watch?v=%s" % youtubeId

    youtubeStreamUrl = getYoutubeStreamUrl(url)
    print(youtubeStreamUrl)    
