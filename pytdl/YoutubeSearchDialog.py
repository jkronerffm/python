from YoutubeSearchBase import Ui_Dialog
from pytube import YouTube
from ytsearch import YoutubeSearch
from ytdl import YoutubeDownload
from VideoDownload import VideoDownload
from PyQt5 import QtWidgets, QtCore, QtGui,QtMultimedia, QtMultimediaWidgets
from PyQt5.QtGui import (QImage, QPixmap, QPainter, QColor)
from PyQt5.QtWidgets import (QApplication,
                             QListWidgetItem,
                             QLabel,
                             QWidget,
                             QMenu,
                             QAction)
from PyQt5.QtMultimedia import (QMediaPlayer, QMediaPlaylist, QMediaContent)
from PyQt5.QtMultimediaWidgets import (QVideoWidget)
from PyQt5.QtCore import (Qt, QSize, QThread, QObject, pyqtSignal)
from threading import Thread
from time import sleep
from ImageLoader import ImageLoader, ImageLoaderThread
import logging

class YoutubeSearchDialog(Ui_Dialog):
    IconSize = QSize(100,100)
    
    def __init__(self):
        self._youtubeSearch = None
        self._urls = []
        self._thread = None
     
    def createWidgetItem(self,data):
        item = QListWidgetItem(data.title)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, data)
        item.setSizeHint(YoutubeSearchDialog.IconSize)
        self._urls.append(data.thumbnail_url)
        self.searchResultList.addItem(item)

    def addIcon(self,index):
        logging.debug("addIcon(index=%d)" % index)
        item = self.searchResultList.item(index)
        pixmap = self._thread.getPixmap(index)
        icon = QtGui.QIcon(pixmap)
        logging.debug("pixmap added to icon")
        item.setIcon(icon)

    def listSearch(self, data):
        self.createWidgetItem(data)

    def pictureAvailable(self, index):
        self.addIcon(index)

    def finished(self):
        pass
    
    def fillList(self, searchPattern):
        for pattern in searchPattern:
            youtubeSearch = YoutubeSearch(pattern)
            youtubeSearch.do(self.listSearch)
        self._thread = ImageLoaderThread(self._urls, YoutubeSearchDialog.IconSize)
        self._thread.pictureAvailable.connect(self.pictureAvailable)
        self._thread.finished.connect(self.finished)
        self._thread.start()
            
    def onClickSearchButton(self):
        self.searchResultList.clear()
        self._urls = []
        searchPattern = self.searchPatternEdit.text().split('|')
        self.fillList(searchPattern)
        
    def getCheckedItems(self):
        checkedItems = []
        for listIndex in range(self.searchResultList.count()):
            item = self.searchResultList.item(listIndex)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item.data(Qt.UserRole))
        return checkedItems
                
    def onLoadAudio(self):
        logging.debug("onLoadAudio")
        checkedItems = self.getCheckedItems()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for item in checkedItems:
            logging.debug(item.title)
            print(f"add item with {item.video_id} to YouTubeDownload")
            videoDownload = VideoDownload(videoId = item.video_id, downloadPath="~/Music/",audioFormat="mp3")
            videoDownload.run()
        QApplication.restoreOverrideCursor()

    def onLoadVideo(self):
        logging.debug("onLoadVideo")
        checkedItems = self.getCheckedItems()

        QApplication.setOverrideCursor(Qt.WaitCursor)

        for item in checkedItems:
            logging.debug(item.title)
            videoDownload = VideoDownload(videoId = item.videoId, downloadPath="~/Video/")
            videoDownload.run()
        QApplication.restoreOverrideCursor()

    def showVideo(self, item):
        data = item.data(Qt.UserRole)
        logging.debug(item.text())
##        logging.debug(dir(data))
        url = data.watch_url
        logging.debug(url)
        player = QMediaPlayer()
        videoWidget = QVideoWidget()
        yt = YouTube(url)
        player.setMedia(stream=yt.streams.first())
        self.horizontalLayout_3.addWidget(videoWidget)
        player.setVideoOutput(videoWidget)
##        videoWidget.show()
        player.play()
        
    def showContextMenu(self,pos):
        currentItem = self.searchResultList.currentItem()
        logging.debug(currentItem.text())
        menu = QMenu()
        action = menu.addAction("Show Video")
        action.triggered.connect(lambda: self.showVideo(currentItem))
        
        menu.exec(self.searchResultList.mapToGlobal(pos))
        
    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.parent = Dialog
        self.searchResultList.setIconSize(YoutubeSearchDialog.IconSize)
        self.searchResultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.searchResultList.customContextMenuRequested.connect(self.showContextMenu)
        self.searchButton.clicked.connect(self.onClickSearchButton)
        self.loadAudioButton.clicked.connect(self.onLoadAudio)
        self.loadVideoButton.clicked.connect(self.onLoadVideo)
        
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.ERROR)
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = YoutubeSearchDialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
