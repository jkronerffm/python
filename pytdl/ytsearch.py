from pytube import Search
from PIL import Image
from io import BytesIO
import sys
import requests

class YoutubeSearch:
    def __init__(self, pattern):
        self.__search = Search(pattern)

    def do(self, list_callback):
        for r in self.__search.results:
            list_callback(r)

    @staticmethod
    def LoadThumbnail(data = None, url = None):
        if (data == None) and (url == None):
            raise AttributeError()
        if url == None:
            url = data.thumbnail_url
        print("LoadThumbnail(url=%s)" % url)
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        if (image == None):
            raise Exception("error on loading thumbnail")
        return image

def listSearch(result):
    print(result.title)
    
if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        s = YoutubeSearch(sys.argv[i])
        s.do(listSearch)

    
