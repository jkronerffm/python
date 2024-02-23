import threading
from RadioPlayer import RadioPlayer
import time
import logging
import sys

class MetaBackgroundWorker:
    CurrentSender = ""
    CurrentTitle = ""
    StopEvent = threading.Event()
    ChangeEvent = threading.Event()
    Lock = threading.Lock()
    
    @staticmethod
    def Create(radioPlayer, callbackFunction):
        logging.debug("Create thread...")
        MetaBackgroundWorker.StopEvent.clear()
        MetaBackgroundWorker.ChangeEvent.clear()
        time.sleep(0.5)
        thread = threading.Thread(target = MetaBackgroundWorker.GetMetaThread, args=(radioPlayer, callbackFunction), daemon = True)
        thread.start()
        
    @staticmethod
    def GetMetaThread(radioPlayer, callbackFunction):
        logging.debug("enter thread")
        currentTitle = ""
        currentSender = ""
        while not MetaBackgroundWorker.StopEvent.is_set():
            try:
                if radioPlayer.media() != None:
                    radioPlayer.media().parse_async()
                    sender = radioPlayer.media().get_meta(0)
                    title = radioPlayer.media().get_meta(12)
                    if not (title != None and title == currentTitle) or sender != currentSender:
                        currentTitle = title
                        currentSender = sender
                        with MetaBackgroundWorker.Lock:
                            callbackFunction(sender, title)
                time.sleep(2)
            except:
                raise
            
        logging.debug("leave thread...")

    @staticmethod
    def HasChanged() -> bool:
        return MetaBackgroundWorker.ChangeEvent.is_set()

    @staticmethod
    def HasStopped() -> bool:
        return MetaBackgroundWorker.StopEvent.is_set()

def metaCallback(sender, title):
    if sender.endswith('.mp3'):
        MetaBackgroundWorker.CurrentTitle = sender[:len(sender)-4].replace('__', ' - ').replace('_', ' ')
        MetaBackgroundWorker.CurrentSender = "playlist"
    else:
        MetaBackgroundWorker.CurrentSender = sender
        MetaBackgroundWorker.CurrentTitle  = title
    MetaBackgroundWorker.ChangeEvent.set()
    
if __name__ == "__main__":
    sender = sys.argv[1] if len(sys.argv) == 2 else "hr1"
        
    logging.basicConfig(level = logging.DEBUG)
    radioPlayer = RadioPlayer("radio.json")
    radioPlayer.play(sender)
    MetaBackgroundWorker.Create(radioPlayer, metaCallback)
    running = True
    logging.debug("start main loop...")
    while running:
        try:
            time.sleep(5)
            if MetaBackgroundWorker.HasChanged():
                with MetaBackgroundWorker.Lock:
                    print("\rsender %s is playing \"%s\"" % (MetaBackgroundWorker.CurrentSender,MetaBackgroundWorker.CurrentTitle), end="")
                    MetaBackgroundWorker.ChangeEvent.clear()
        except KeyboardInterrupt:
            running = False

    MetaBackgroundWorker.StopEvent.set()
    radioPlayer.stop()
    logging.debug("leave __main__")
