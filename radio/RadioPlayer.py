import vlc
import time
import json
import logging
from playYoutube import getYoutubeStreamUrl
from fileListRandomizer import shufflePlayList
import threading

class RadioPlayer:

    def __init__(self, configFile):
        self._senderData = {}
        self.readConfigFile(configFile)
        self._instance = vlc.Instance()
        self._player = self._instance.media_list_player_new()

    def background(self):
        return self._senderData['background']
    
    def readConfigFile(self, configFile):
        with open(configFile) as jsonFile:
            self._senderData = json.load(jsonFile)
            w = len(self.sender())
            self._currentSender = self.sender()[0]

    def senderData(self):
        return self._senderData

    def sender(self):
        return self._senderData['sender']
    
    def currentSender(self):
        return self._currentSender

    def player(self):
        if self._player == None:
            self._player = self._instance.media_list_player_new()
        return self._player

    def mediaPlayer(self):
        return self.player().get_media_player()

    def media(self):
        return self.mediaPlayer().get_media()
    
    def play(self, senderName):
        logging.debug("play(sender=%s)" % (senderName))
        sender = self.getSenderByName(senderName) if self.hasSenderWithName(senderName) else self.getSenderByName("my music")
        
        if sender["name"] == "my music":
            self.playRandomized(sender["url"])
        else:
            url = sender["url"]
            if "youtube" in url:
                url = getYoutubeStreamUrl(url)
            self.playUrl(url)

    def playRandomized(self,url):
        songs = shufflePlayList(url)
        self.stop()
        mediaList = self._instance.media_list_new()
        for song in songs:
            media = self._instance.media_new(song)
            mediaList.add_media(media)
        self.player().set_media_list(mediaList)
        self.player().play()
        
    def playUrl(self, url):
        logging.debug("playUrl(url=%s)" % url)
        self.stop()
        mediaList = self._instance.media_list_new()
        if isinstance(url, list):
            for item in url:
                media = self._instance.media_new(item)
                mediaList.add_media(media)
        else:
            media = self._instance.media_new(url)
            mediaList.add_media(media)
        self.player().set_media_list(mediaList)
        self.player().play()

    def playYoutube(self, url):
        logging.debug("playYoutube(url=\"%s\")" % url)
        stream_url = getYoutubeStreamUrl(url)
        logging.debug(stream_url)
        self.playUrl(stream_url)
        
    def stop(self):
        self.player().stop()

    def getSenderByName(self, senderName):
        for sender in self.sender():
            if sender["name"] == senderName:
                return sender
        return None
    
    def hasSenderWithName(self, senderName):
        return self.getSenderByName(senderName) != None
            
    def pause(self):
        self.player().pause()
        
    def setVolume(self, value):
        logging.debug("setVolume(value=%d)" % value)
        self.mediaPlayer().audio_set_volume(value)

    def getVolume(self):
        return self.mediaPlayer().audio_get_volume()

def getMetaThread(radioPlayer, callbackFunction, ev):
    print("enter thread...")
    currentTitle = ""
    while not ev.is_set():
        try:
            time.sleep(2)
            media.parse_async()
            sender = radioPlayer.media().get_meta(0)
            title = radioPlayer.media().get_meta(12)
            if title != currentTitle:
                callbackFunction(sender, title)
                currentTitle = title
            time.sleep(3)
        except:
            pass
    print("leave thread...")

def metaCallback(sender, title):
    print(f"sender {sender} is playing \"{title}\"")
        
if __name__ == "__main__":
    ev = threading.Event()
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer("radio.json")
    radioPlayer.play("ffh")
    radioPlayer.setVolume(50)
    media=radioPlayer.media()
    time.sleep(5)
    ev.clear()
    t = threading.Thread(target = getMetaThread, args=(radioPlayer, metaCallback, ev))
    t.run()
    running = True
    while running:
        print(".", end="")
        try:
            sleep(5)
        except KeyboardInterrupt:
            running = False
    ev.set()
    radioPlayer.stop()
