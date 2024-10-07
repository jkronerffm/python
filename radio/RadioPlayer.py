import vlc
import time
import json
import logging
#from playYoutube import getYoutubeStreamUrl
from fileListRandomizer import shufflePlayList
from Equalizer import Equalizer
import threading
import ctypes
from ctypes import *

class VlcPlayerFactory:
    Player = None
    
    @staticmethod
    def createPlayer(vlcInstance):
        if VlcPlayerFactory.Player != None:
            VlcPlayerFactory.Player.stop()
            VlcPlayerFactory.Player = None
        VlcPlayerFactory.Player = vlcInstance.media_list_player_new()

        return VlcPlayerFactory.Player

class RadioPlayer:
    CurrSender = ""
    CurrTitle = ""
    LocalList = "wakeUp"
    BlockEvents = True
    
    def __init__(self, configFile):
        self._senderData = {}
        self.readConfigFile(configFile)
        self._instance = vlc.Instance()
        self._player = None #self._instance.media_list_player_new()
        self._equalizerIndex = -1
        self._playerStopEventHandler = []
        self._playerNextItemHandler = []
        self._stopping = False

    @property
    def stopping(self):
        return self._stopping

    @stopping.setter
    def stopping(self, value):
        self._stopping = value
        
    def addPlayerStopEventHandler(self, eventHandler):
        logging.debug("####### addPlayerStopEventHandler()")
        self._playerStopEventHandler.append(eventHandler)

    def addPlayerListNextItemHandler(self, eventHandler):
        self._playerNextItemHandler.append(eventHandler)
        
    def fireListPlayerPlayed(self, event, player, senderName):
        logging.debug(f"####### RadioPlayer.fireListPlayerPlayed {senderName}")
        for eventHandler in self._playerStopEventHandler:
            eventHandler(event, player)
        
    def fireListEndReached(self, event, player, senderName):
        logging.debug(f"####### RadioPlayer.fireListEndReached  {senderName}")

    def fireListPlayerNextItemSet(self, event, player, senderName):
        logging.debug(f"####### RadioPlayer.fireListPlayerNextItemSet {senderName}")
        for eventHandler in self._playerNextItemHandler:
            eventHandler(player)
            
    def setMediaPlayerStopEvent(self, senderName):
        if not RadioPlayer.BlockEvents:
            player = self.player()
            em = player.event_manager()
            logging.debug("###### setMediaPlayerStopEvent()")
            em.event_attach(vlc.EventType.MediaListEndReached, self.fireListEndReached, player, senderName)
            em.event_attach(vlc.EventType.MediaListPlayerPlayed, self.fireListPlayerPlayed, player, senderName)
            em.event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.fireListPlayerNextItemSet, player, senderName)
        
    def clearMediaPlayerStopEvent(self):
        mediaPlayer = self.player()
        eventManager = mediaPlayer.event_manager()
        eventManager.event_detach(vlc.EventType.MediaListEndReached)
        eventManager.event_detach(vlc.EventType.MediaListPlayerPlayed)
        eventManager.event_detach(vlc.EventType.MediaListPlayerNextItemSet)

    def equalizerIndex(self):
        return self._equalizerIndex

    def background(self):
        return self._senderData['background']

    def icon(self):
        return self._senderData['icon']
    
    def timeColor(self):
        return self._senderData['timecolor']
        
    def brightness(self):
        return int(self._senderData['brightness']) / 100

    def remoteControl(self):
        return self._senderData['remotecontrol']
    
    def imageWidth(self):
        return int(self._senderData['imageWidth']) if 'imageWidth' in self._senderData else 64
    
    def readConfigFile(self, configFile):
        with open(configFile) as jsonFile:
            self._senderData = json.load(jsonFile)
            w = len(self.sender())
            self._currentSender = self.sender()[0]

    def senderData(self):
        return self._senderData

    def sender(self):
        return self._senderData['sender']

    def repeat(self, senderName):
        self.stop()
        self.play(senderName)

    def getNextSender(self, senderName):
        senderList = self.sender()
        index = [index for index, sender in enumerate(senderList) if sender['name'] == senderName][0]
        logging.debug(f"getNextSender(index={index}, senderName={senderName})")
        index = index + 1 if index < (len(senderList) - 1) else 0
        nextSender = senderList[index]
        logging.debug(f"getNextSender(senderName={senderName}) => {nextSender}")
        return nextSender

    def getPreviousSender(self, senderName):
        senderList = self.sender()
        index = [index for index, sender in enumerate(senderList) if sender['name'] == senderName][0]
        logging.debug(f"getNextSender(index={index}, senderName={senderName})")
        index = index - 1 if index > 0 else (len(senderList)-1)
        previousSender = senderList[index]
        return previousSender
    
    def urlEndsWith(self, name):
        for senderItem in self.sender():
            if senderItem["url"].endswith(name):
                return senderItem
        return None
        
    def currentSender(self):
        return self._currentSender

    def player(self):
        if self._player == None:
            self._player = VlcPlayerFactory.createPlayer(self._instance)
#        logging.debug(f"player({self._player})")
        return self._player

    def mediaPlayer(self):
        return self.player().get_media_player()

    def media(self):
        return self.mediaPlayer().get_media()
    
    def play(self, senderName):
        logging.debug("play(senderName=%s)" % (senderName))
        sender = self.getSenderByName(senderName) if self.hasSenderWithName(senderName) else self.getSenderByName(RadioPlayer.LocalList)
        logging.debug(f"play(sender={sender}, shuffle={'shuffle' in sender and sender['shuffle']})")
        self.clearMediaPlayerStopEvent()
        self._player = VlcPlayerFactory.createPlayer(self._instance)
        
        self.setMediaPlayerStopEvent(senderName)
        if "shuffle" in sender and sender["shuffle"]:
            self.playRandomized(sender["url"])
        else:
            url = sender["url"]
            if "youtube" in url:
                print("youtube cannot be played. Sorry...")
                return
                #url = getYoutubeStreamUrl(url)
            self.playUrl(url)
        logging.debug(f"play -> setMediaPlayerStopEvent({senderName}) BlockEvents={RadioPlayer.BlockEvents}")

    def playRandomized(self,url):
        songs = shufflePlayList(url)
#        self.stop()
        mediaList = self._instance.media_list_new()
        for song in songs:
            media = self._instance.media_new(song)
            mediaList.add_media(media)
        self.player().set_media_list(mediaList)
        self.player().play()
        
    def playUrl(self, url,blocking=False):
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
        logging.debug("playUrl()-> call setMediaPlayerStopEvent()")
        self.player().play()
        if blocking:
            time.sleep(1)
            duration = self.mediaPlayer().get_length() / 1000
            logging.debug(f"playUrl(url={url}, duration={duration})")
            time.sleep(duration)

    def playYoutube(self, url):
        logging.debug("playYoutube(url=\"%s\")" % url)
        stream_url = getYoutubeStreamUrl(url)
        logging.debug(stream_url)
        self.playUrl(stream_url)
        
    def stop(self):
        self.player().stop()
        self.stopping = False

    def next(self):
        self.player().next()
        
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

    def incrementEqualizer(self):
        equalizerInstance = Equalizer.GetInstance()
        if self.equalizerIndex() < equalizerInstance.getPresetCount():
            self._equalizerIndex += 1
        else:
            self._equalizerIndex = 0
        
    def decrementEqualizer(self):
        equalizerInstance = Equalizer.GetInstance()
        if self.equalizerIndex() > 0:
            self._equalizerIndex -= 1
        else:
            self._equalizerIndex = equalizerInstance.getPresetCount() - 1
            
    def nextEqualizer(self):
        equalizerInstance = Equalizer.GetInstance()
        self.incrementEqualizer()
        equalizer = equalizerInstance.getEqualizerByIndex(self.equalizerIndex())
        self.mediaPlayer().set_equalizer(equalizer)

    def previousEqualizer(self):
        equalizerInstance = Equalizer.GetInstance()
        self.decrementEqualizer()
        equalizer = equalizerInstance.getEqualizerByIndex(self.equalizerIndex())
        self.mediaPlayer().set_equalizer(equalizer)
    
    def initEqualizer(self):
        self.setEqualizerByIndex(11)

    def setEqualizerByIndex(self, index):
        equalizerInstance = Equalizer.GetInstance()
        equalizer = equalizerInstance.getEqualizerByIndex(index)
        logging.debug(f"Equalizer.setEqualizerByName(index={index}, equalizer={equalizer})")
        self.mediaPlayer().set_equalizer(equalizer)
        self._equalizerIndex = index

    def setEqualizerByName(self, name):
        equalizerInstance = Equalizer.GetInstance()
        equalizer = equalizerInstance.getEqualizerByName(name)
        logging.debug(f"Equalizer.setEqualizerByName(name={name}, equalizer={equalizer})")
        self.mediaPlayer().set_equalizer(equalizer)
        self._equalizerIndex = equalizer.getPresetIndex(name)
        
    @staticmethod
    def GetMetaThread(radioPlayer, stopEvent, changeEvent):
        logging.debug("enter thread...")
        currentTitle = ""
        while not stopEvent.is_set():
            try:
                time.sleep(2)
                media.parse_async()
                sender = radioPlayer.media().get_meta(0)
                title = radioPlayer.media().get_meta(12)
                if title != currentTitle:
                    callbackFunction(sender, title, changeEvent)
                    currentTitle = title
            except:
                logging.debug("caught exception")
                raise
        logging.debug("leave thread...")


    def startMetaParsing(self, stopEvent, changeEvent):
        stopEvent.clear()
        changeEvent.clear()
        self._thread = threading.Thread(target = RadioPlayer.GetMetaThread, args=(self, stopEvent, changeEvent))
        self._thread.start()
        logging.debug("leave startMetaParsing")

    @staticmethod
    def MetaCallback(sender, title, changeEvent):
        RadioPlayer.CurrSender = sender
        RadioPlayer.CurrTitle = title
        changeEvent.set()

@vlc.CallbackDecorators.VideoLockCb
def _lockcb(opaque, planes):
    print("lock")
    return ctypes.create_string_buffer('\000')

@vlc.CallbackDecorators.VideoUnlockCb
def _unlockcb(opoaque, pic, planes):
    print("unlock")
    return ctypes.create_string_buffer('\000')

@vlc.CallbackDecorators.VideoDisplayCb
def _displaycb(opaque, picture):
    print("display")
    return ctypes.create_string_buffer('\000')

@vlc.CallbackDecorators.AudioPlayCb
def playcb(opaque, samples, count, pts):
    print(f"playcb(opaque={opaque},samples={samples},count={count}, pts={pts})")
    return ctypes.create_string_buffer(b'\000')

def titleChanged(event):
    print(event)
    
a= ctypes.create_string_buffer(b'\000' * 2048)

def nextItem(player):
    global radioPlayer
    logging.debug("nextItem")
    time.sleep(3)
    logging.debug("--> stop")
    radioPlayer.stop()
    logging.debug("--> next")
    radioPlayer.next()
    logging.debug("leave nextItem")

if __name__ == "__main__":
    stopEvent = threading.Event()
    changeEvent = threading.Event()
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer("/var/radio/conf/radio.json")
    nextSender = radioPlayer.getNextSender("hr1")
    previousSender = radioPlayer.getPreviousSender("hr1")
    nextSender = radioPlayer.getNextSender(previousSender['name'])
    events = radioPlayer.player().event_manager()
    events.event_attach(vlc.EventType.MediaPlayerTitleChanged, titleChanged)
    devices = radioPlayer.mediaPlayer().audio_output_device_enum()
    if devices:
        devs = []
        device = devices
        print(dir(device.contents))
        while device:
            print(device.contents.description)
            device = device.contents.next
    print("=" * 80)
    print(dir(radioPlayer.mediaPlayer()))
##    radioPlayer.mediaPlayer().video_set_callbacks(_lockcb, _unlockcb, _displaycb, a)
##    radioPlayer.mediaPlayer().audio_set_callbacks(play=playcb, pause=None, resume=None, flush=None, drain=None, opaque=None)
    nextSender = radioPlayer.getNextSender("stereo joya")
    nextSender = radioPlayer.getNextSender(nextSender['name'])
#    nextSender = radioPlayer.getNextSender(nextSender['name'])
    logging.debug(f"play {nextSender}")
    radioPlayer.setVolume(50)
    RadioPlayer.BlockEvents = False
    radioPlayer.addPlayerListNextItemHandler(nextItem)
    
    radioPlayer.play(nextSender['name'])
    logging.debug("wait for interrupt...")
    while True:
        try:
             time.sleep(1)
        except KeyboardInterrupt:
            break;
        
##    radioPlayer.play("radio maria")
##    radioPlayer.setVolume(50)
##    media=radioPlayer.media()
##    time.sleep(5)
##    radioPlayer.startMetaParsing(stopEvent, changeEvent)
##    running = True
##    logging.debug("enter main loop")
##    while running:
##        print(".", end="")
##        try:
##            time.sleep(2)
##            if changeEvent.is_set():
##                print("\rsender %s is playing \"%s\"" %(RadioPlayer.CurrSender,RadioPlayer.CurrTitle), end="", flush=True)
##                changeEvent.clear()
##        except KeyboardInterrupt:
##            running = False
##    stopEvent.set()
    radioPlayer.stop()
