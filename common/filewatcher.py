import os
import threading
import time
import logging
import signal
import fcntl
from pathlib import Path
import datetime

class WatchDog:
    StopEvent = threading.Event()
    ChangeEvent = threading.Event()
    Lock = threading.Lock()
    Instance = None
    Done = False
    _filePathList = {}
    
    def __init__(self):
        pass

    @staticmethod
    def GetInstance():
        if WatchDog.Instance == None:
            WatchDog.Instance = WatchDog()

        return WatchDog.Instance

    @staticmethod
    def Handler(signum, dirname):
        if WatchDog.Done:
            WatchDog.Done = False
            return

        logging.debug(f"WatchDog.Handler(signum={signum},dirname={dirname})")
        WatchDog.Done = True
        path = Path(dirname)
        files = list(path.iterdir())
        lastTime = 0
        changedFile = ""
        for file in files:
            mtime = os.path.getmtime(file)
            if mtime > lastTime:
                lastTime = mtime
                changedFile = str(file)

        instance = WatchDog.GetInstance()
        instance.fireEvent(changedFile, datetime.datetime.fromtimestamp(lastTime, datetime.timezone.utc))

    def watch(self, filepath, handler):    
        dirname = os.path.dirname(filepath)
        if len(self._filePathList) == 0:
            signal.signal(signal.SIGIO, lambda signum, frame: WatchDog.Handler(signum, dirname))
        self._filePathList[filepath] = handler
        fd = os.open(dirname, os.O_RDONLY)
        fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(fd, fcntl.F_NOTIFY,
                    fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

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

    def getHandler(self, filepath):
        return None if not filepath in self._filePathList else self._filePathList[filepath]
    
    def fireEvent(self,changedFile, modifiedTime):
        logging.debug(f"fireEvent(changdFile={changedFile}, modifiedTime={str(modifiedTime)})")
        handler = self.getHandler(changedFile)
        if handler != None:
            handler(changedFile, modifiedTime)

def waketime_handler(changedFile, modifiedTime):
    logging.debug(f"waketime_handler(changedFille={changedFile}, modifiedTime={str(modifiedTime)})")

def radio_handler(changedFile, modifiedTime):
    logging.debug(f"radio_handler(changedFille={changedFile}, modifiedTime={str(modifiedTime)})")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dirname = "/var/radio/conf/"

    watchDog = WatchDog.GetInstance()
    watchDog.watch(os.path.join(dirname, "waketime.json"),  waketime_handler)
    watchDog.watch(os.path.join(dirname, "radio.json"), radio_handler)
    isWaiting = True
    while isWaiting:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            isWaiting = False

    WatchDog.Stop()
