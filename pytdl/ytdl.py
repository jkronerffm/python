from pytube import YouTube
import sys,os, subprocess
import Home

class YoutubeDownload:
    def __init__(self, url = None, youtube = None):
        if (url == None) and (youtube == None):
            raise AttributeError()
        
        if (url != None):
            self._youtube = YouTube(url)
        else:
            self._youtube = youtube
        self._youtube.register_on_complete_callback(self.complete_function)
        self._youtube.register_on_progress_callback(self.progress_function)
        self._downloadType = "video"

    def convert(self, filePath, outputPath, extension):
        (filename, ext) = os.path.splitext(os.path.basename(filePath))
        outputFilepath = os.path.join(outputPath, filename + extension)
        print("convert file to %s" % outputFilepath)
        subprocess.run([
            'ffmpeg',
            '-i', filePath,outputFilepath])

    def completeAudio(self, filePath):
        outputPath = self.getOutputPath('Music')
        self.convert(filePath, outputPath, '.mp3')
        os.remove(filePath)

    def completeVideo(self, filePath):
        outputPath = self.getOutputPath('Videos')
        self.convert(filePath, outputPath, '.mp4')
        os.remove(filePath)
        pass
    
    def complete_function(self, stream, filePath):
        print("\ndownload for %s completed." % filePath)
        if (self._downloadType == "audio"):
            self.completeAudio(filePath)
        else:
            self.completeVideo(filePath)
        
    def progress_function(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        p = self.percent((size-bytes_remaining), size)
        print (str(p)+'%\r', end='')

    def percent(self, tem, total):
        perc = (float(tem) / float(total)) * float(100)
        return perc

    def home(self):
        home = Home.Home()
        return home()

    def loadAudio(self):
        print("loadAudio")
            
        print("filter streams for audio")
        stream = self._youtube.streams.get_audio_only()
        print("start download of file %s..." % stream.title)
        self._downloadType = "audio"
        stream.download(output_path="/tmp/youtube")

    def loadVideo(self):
        print("loadVideo")
        self.downloadType = "video"
        stream = self._youtube.streams.first()
        stream.download(output_path="/tmp/youtube")
    
    def getOutputPath(self, directory):
        home = self.home()
        outputPath = os.path.join(home, directory)
        return outputPath
    
##    def getNewFilename(self,filepath, extension):
##        home = self.home()
##        print("home: %s" % home)
##        dirname = os.path.join(home, 'Music')
##        (filename,ext) = os.path.splitext(filepath)
##        newFilename = os.path.join(dirname, filename + extension)
##        return newFilename
        
if __name__ == "__main__":
    url = sys.argv[1]
    ytl = YoutubeDownload(url)
    ytl.loadAudio()
        
    
