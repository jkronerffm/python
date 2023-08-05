from pytube import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtWidgets import *
from math import *
from pytube import YouTube
import sys,os, time

class DownloadThread(QThread):
    finished = pyqtSignal()
    loading = pyqtSignal()
    
    def __init__(self, url, downloadPath):
        super().__init__()
        self._url = url
        self._filename = None
        self._downloadPath = downloadPath

    def run(self):
        yt = YouTube(self._url)
        stream = yt.streams.first()
        self._filename = stream.default_filename
        print("DownloadThread.run(filename=%s)" % self._filename)
        self.loading.emit()
        stream.download(self._downloadPath)
        self.finished.emit()

    def downloadPath(self):
        return self._downloadPath

    def filename(self):
        return self._filename
    
    def filePath(self):
        return os.path.join(self.downloadPath(), self.filename())
    
class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.layout = QVBoxLayout(self)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setSizePolicy(sizePolicy)
        self.buttonWidget = QWidget(self)
        self.hLayout = QHBoxLayout(self.buttonWidget)
        self.loadButton = QPushButton("open Video")
        self.playButton = QPushButton()
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0,0)
        self.durationLabel = QLabel()
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(QSize(16,16))
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.hLayout.addWidget(self.loadButton)
        self.hLayout.addWidget(self.playButton)
        self.hLayout.addWidget(self.positionSlider)
        self.hLayout.addWidget(self.durationLabel)
        self.buttonWidget.setLayout(self.hLayout)
        self.setLayout(self.layout)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.stateChanged.connect(self.onMediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.onPositionChanged)
        self.mediaPlayer.durationChanged.connect(self.onDurationChanged)                        
        self.statusbar = QStatusBar()
        self.statusbar.setFixedHeight(14)
        self.playButton.setEnabled(False)
        self.loadButton.clicked.connect(self.onLoadFile)
        self.playButton.clicked.connect(self.onPlayVideo)
        self.layout.addWidget(self.videoWidget)
        self.layout.addWidget(self.buttonWidget)
        self.layout.addWidget(self.statusbar)
        self.setAcceptDrops(True)
        self.show()    

    def onFinished(self):
        print("onFinished...")
        
    def onLoading(self):
        print("onLoading()...")
        path = self.downloadThread.filePath()
        filepath = self.downloadThread.filePath()
        self.videoLength = 0
        self.setMediaFile(filepath)
        self.mediaPlayer.play()

    def dropEvent(self, event):
        url = event.mimeData().text()
        print("received %s" % url)
        self.downloadThread = DownloadThread(url, "/tmp")
        self.downloadThread.loading.connect(self.onLoading)
        self.downloadThread.finished.connect(self.onFinished)
        self.downloadThread.start()
        
    def dragEnterEvent(self, event):
        url = event.mimeData().text()
        if "https://www.youtube.com/watch?" in url:
            event.setAccepted(True)
            event.setDropAction(Qt.CopyAction)
        
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
        
    def onDurationChanged(self, duration):
        print("onDurationChanged(duration=%d)" % (duration))
        self.videoLength = duration
        self.positionSlider.setRange(0, duration)
        
    def onPositionChanged(self, position):
        self.positionSlider.setValue(position)
        if self.videoLength == 0:
            self.videoLength = position * 2
        remainingLength = (float(self.videoLength) - float(position)) / 1000.0 / 60.0
        remainingMinutes = floor(remainingLength)
        remainingSeconds = (remainingLength - remainingMinutes) * 60
        remainingTime = "%d:%02d" % (remainingMinutes, remainingSeconds)
        self.durationLabel.setText(remainingTime)
        
    def onMediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
                
    def onPlayVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
        
    def onLoadFile(self):
        filename,_ = QFileDialog.getOpenFileName(self,'Open video','/home/ubuntu/Videos','Videos(*.mp4);All files(*.*)', '*.mp4')
        if filename != '':
            self.setMediaFile(filename)
            
    def setMediaFile(self, filename):
        url = QUrl.fromLocalFile(filename)
        self.statusbar.showMessage(os.path.basename(filename))
        self.mediaPlayer.setMedia(QMediaContent(url))
        self.playButton.setEnabled(True)
        
if __name__ == "__main__":         
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()
