import vlc
import time
import json
import logging
from playYoutube import getYoutubeStreamUrl

class RadioPlayer:

    def __init__(self, configFile):
        self._senderData = {}
        self._player = None
        self.readConfigFile(configFile)

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
            inst = vlc.Instance()
            self._player = inst.media_list_player_new()
        return self._player
    
    def playUrl(self, urlList):
        logging.debug("play url %s" % urlList)
        inst = vlc.Instance()
        mediaList = inst.media_list_new(urlList)
        self.stop()
        self.player().set_media_list(mediaList)
        self.player().play()

    def playYoutube(self, url):
        logging.debug("playYoutube(url=\"%s\")" % url)
        stream_url = getYoutubeStreamUrl(url)
        logging.debug(stream_url)
        self.playUrl([stream_url])
        
    def stop(self):
        self.player().stop()

    def getSenderByName(self, senderName):
        for sender in self.sender():
            if sender["name"] == senderName:
                return sender
            
    def play(self, senderName):
        logging.debug("player sender %s" % (senderName))
        sender = self.getSenderByName(senderName)
        url = sender["url"]
        if "youtube" in url:
            url = getYoutubeStreamUrl(url)
        self.playUrl([url])
      
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer("radio.json")
    sender = radioPlayer.getSenderByName("hr1")
    radioPlayer.play("hr1")
