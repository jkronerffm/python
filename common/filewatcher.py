import os
import threading
import time
from inotify_simple import INotify, flags
import logging

class WatchDog:
    StopEvent = threading.Event()
    ChangeEvent = threading.Event()
    Lock = threading.Lock()
    Instance = None
    _events = []
    def __init__(self):
        pass

    @staticmethod
    def GetInstance():
        if WatchDog.Instance == None:
            WatchDog.Instance = WatchDog()

        return WatchDog.Instance

    @staticmethod
    def CreateInstance(filepath):
        instance = WatchDog.GetInstance()
        instance.watch(filepath)
        return instance

    @staticmethod
    def Watch(inotify):
        logging.debug("start thread...")
        while not WatchDog.HasStopped():
            try:
               time.sleep(1)
               hasChanged = False
               for event in inotify.read():
                   logging.debug(f"WatchDog.Watch(event={event})")
                   WatchDog.Handler(event)
                   hasChanged = True
               if hasChanged:
                   WatchDog.Change()
            except:
                raise
            
        logging.debug("leave thread...")
        
    def watch(self,filepath):
        self._filepath = filepath
        inotify = INotify()
        inotify.add_watch(filepath, flags.DELETE | flags.MODIFY | flags.DELETE_SELF)
        WatchDog.StopEvent.clear()
        WatchDog.ChangeEvent.clear()
        thread = threading.Thread(target = WatchDog.Watch, args=(inotify,), daemon=True)
        thread.start()

    def get_handler(self):
        return self._handler

    def get_filepath(self):
        return self._filepath

    def addEvent(self,event):
        self._events.append(event)

    def popEvent(self):
        with WatchDog.Lock:
            event = None if len(self._events) == 0 else self._events.pop()

        return event
    
    @staticmethod
    def Handler(event):
        logging.debug(f"WatchDog.Handler(event={event})")
        with WatchDog.Lock:
            WatchDog.GetInstance().addEvent(event)

    @staticmethod
    def Change():
        WatchDog.ChangeEvent.set()
        
    @staticmethod
    def Stop():
        WatchDog.StopEvent.set()

    @staticmethod
    def HasStopped():
        return WatchDog.StopEvent.is_set()

    @staticmethod
    def HasChanged():
        return WatchDog.ChangeEvent.is_set()
        
def handler(watchDog):
    logging.debug(f"handler(watchDog={watchDog})")
    event = watchDog.popEvent()
    while event != None:
        print(event)
        event = watchDog.popEvent()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    filepath = "/var/radio/conf/"

    WatchDog.CreateInstance(filepath)
    isWaiting = True
    while isWaiting:
        try:
            time.sleep(2)
            if WatchDog.HasChanged():
                handler(WatchDog.GetInstance())
                WatchDog.ChangeEvent.clear()
        except KeyboardInterrupt:
            isWaiting = False

    WatchDog.Stop()
