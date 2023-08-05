from ytsearch import YoutubeSearch
from PIL import Image, ImageQt
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import (QImage, QPixmap, QPainter, QColor)
from PyQt5.QtCore import (Qt, QSize, QThread)
from io import BytesIO
from time import sleep
import requests, sys, logging

class ImageLoaderThread(QThread):
    pictureAvailable = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    
    def __init__(self, urls, size = None):
        super().__init__()
        self._urls = urls
        self._size = size
        self._pixmaps = {}
        
    def run(self):
        for index in range(len(self._urls)):
            url = self._urls[index]
            logging.debug("load image #%d from %s" % (index, url))
            sleep(0.5)
            pixmap = ImageLoader.LoadPixmap(url, self._size)
            self._pixmaps[index] = pixmap
            logging.debug("LoadPixmap returned %s" % (pixmap != None))
            self.pictureAvailable.emit(index)
        logging.debug("finished loop")
        self.finished.emit()

    def getPixmap(self, index):
        return self._pixmaps[index]
            
class ImageLoader:
    @staticmethod
    def LoadPixmap(url, size = None):
        logging.debug("LoadPixmap(url=%s, size=%s)" % (url, size))
        image = ImageLoader.LoadWebImage(url)
        qim = ImageQt(image)
        if (qim == None):
            raise Exception("ImageQt failed!")
        pix = QPixmap.fromImage(qim)
        if (size != None):
            mask = QPixmap(size)
            mask.fill(QtGui.QColor(255,255,255,0))
            painter = QPainter()
            painter.begin(mask)
            painter.setBackgroundMode(Qt.TransparentMode)
            sizedPix = pix.scaled(size, Qt.KeepAspectRatio)
            pixSize=sizedPix.size()
            deltaSize = (size - pixSize) / 2
            point = QtCore.QPoint(deltaSize.width(),deltaSize.height())
            painter.drawPixmap(point, sizedPix)
            painter.end()
            resultPix = mask
        else:
            resultPix = pix
        return resultPix

    @staticmethod
    def maskPixmap(pix):
        mask = QImage(size, QImage.Format_ARGB32)
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        pixSize = sizedPix.size()
        x = int((size.width() - pixSize.width()) / 2)
        y = int((size.height() - pixSize.height()) / 2)
        painter.drawPixmap(x, y, sizedPix)
        resultPix = QPixmap.fromImage(mask)

    @staticmethod
    def LoadWebImage(url):
        logging.debug("LoadWebImage(url=%s)" % url)
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        if (image == None):
            raise Exception("error on loading webimage")
        return image

def pictureAvailable(index):
    print("picture #%d is available" % (index))

def finished():
    print("Load process is finished")

def acceptDialog():
    quit()

def rejectDialog():
    quit()
    
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    logging.basicConfig(level=logging.DEBUG)
    urls = ["https://i.ytimg.com/vi/-1pMMIe4hb4/hqdefault.jpg",
            "https://i.ytimg.com/vi/EK_LN3XEcnw/sddefault.jpg",
            "https://i.ytimg.com/vi/2iC8CRKxvmQ/hqdefault.jpg?sqp=-oaymwEmCOADEOgC8quKqQMa8AEB-AHUBoAC4AOKAgwIABABGH8gEygbMA8=&rs=AOn4CLCnyohTopovDuYVDEfsk6Ih79Vf6Q",
            "https://i.ytimg.com/vi/A5WSqWJ4obg/sddefault.jpg"]
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Test")
    layout = QtWidgets.QVBoxLayout(dialog)
    size = QtCore.QSize(100,100)
    label = QtWidgets.QLabel("Label")
    label.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),size))
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
##    image = ImageLoader.LoadWebImage(urls[0])
##    qim = ImageQt(image)
##    pixmap = QtGui.QPixmap.fromImage(qim)
##    sizedPix = pixmap.scaled(size,Qt.KeepAspectRatio)
##    ppix = QtGui.QPixmap(size)
##    color = QtGui.QColor(255,255,255,0)
##    ppix.fill(color)
##    painter = QtGui.QPainter(ppix)
    ppix = ImageLoader.LoadPixmap(urls[0], size)
##    pixSize = sizedPix.size()
##    p = (size - pixSize) / 2
##    painter.drawPixmap(p.width(), p.height(), pixSize.width(), pixSize.height(), sizedPix)
    label.setPixmap(ppix)
##    print("%s - %s = %s" % (size, pixSize,p))
    buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    buttonBox.accepted.connect(acceptDialog)
    buttonBox.rejected.connect(rejectDialog)
    layout.addWidget(buttonBox)
    dialog.show()
##    thread = ImageLoaderThread(urls, QSize(150,100))
##    thread.pictureAvailable.connect(pictureAvailable)
##    thread.finished.connect(finished)
##    thread.start()
##    
##    thread.wait()
    app.exec()

    print("After waiting loop")
