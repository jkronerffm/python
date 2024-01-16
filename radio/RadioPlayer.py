import vlc
import time
import json
import logging
from playYoutube import getYoutubeStreamUrl
from fileListRandomizer import shufflePlayList

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
    
    def play(self, senderName):
        logging.debug("play(sender=%s)" % (senderName))
        sender = self.getSenderByName(senderName)
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

    def pause(self):
        self.player().pause()
        
    def setVolume(self, value):
        logging.debug("setVolume(value=%d)" % value)
        self.mediaPlayer().audio_set_volume(value)

    def getVolume(self):
        return self.mediaPlayer().audio_get_volume()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer("radio.json")
    sender = radioPlayer.getSenderByName("my music")
    radioPlayer.playRandomized(sender["url"])
    radioPlayer.setVolume(50)
    time.sleep(30)
    radioPlayer.stop()
