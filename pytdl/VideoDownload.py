import sys
import os
import logging

class VideoDownload:
    def __init__(self, videoId, **args):
        self._videoId = videoId
        
        self.downloadPath = args['downloadPath'] if 'downloadPath' in args else None
        self.audioFormat = args['audioFormat'] if 'audioFormat' in args else None
        
    @property
    def audioFormat(self):
        return self._audioFormat

    @audioFormat.setter
    def audioFormat(self, value):
        self._audioFormat = value
        
    @property
    def downloadPath(self):
        return self._downloadPath

    @downloadPath.setter
    def downloadPath(self, value):
        self._downloadPath = value
        
    @property
    def videoId(self):
        return self._videoId

    @videoId.setter
    def videoId(self, value):
        self._videoId = value

    @property
    def url(self):
        if self.videoId == None:
            raise RuntimeError("VideoId is not initialized")

        return f"https://youtube.com/watch?v={self.videoId}"
    
    @property
    def command(self):
#        return "youtube-dl"
        return "yt-dlp"
    
    def _getCommand(self):
        command = f"{self.command} {self.url}"
        command += f" -x --audio-format {self.audioFormat}" if self.audioFormat != None else ""
        command += f" -P {self.downloadPath}" if self.downloadPath != None else ""
        return command
    
    def _getTitle(self):
        command = f"{self.command} --print \"%(title)s\" {self.url}"
        self._title = os.popen(command).read()
        return self._title
        
    def run(self):
        os.system(self._getCommand())

if __name__ == "__main__":
    dv = VideoDownload(sys.argv[1], downloadPath="~/Music/wakeUp", audioFormat="mp3")
    dv.run()
    
