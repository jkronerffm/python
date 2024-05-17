import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..', 'common'))
from FileSelector import FileSelector
import pygame

class Sprite:
    FileSelector = FileSelector(os.path.join(os.getcwd(), 'images'), ['png', 'jpg', 'svc'])
    def __init__(self, imagenames, pos = (0, 0), size = None):
        self._images = {}
        for imagename in imagenames:
            imagepath = Sprite.FileSelector.select(imagename)
            image = pygame.image.load(imagepath)
            if size == None:
                self._images[imagename] = image
            else:
                self._images[imagename] = pygame.transform.scale(image, size)
        self._pos = pos
        self._size = size
        self._currentImage = 0

    @property
    def currentImage(self):
        return self._currentImage

    @currentImage.setter
    def currentImage(self, value):
        self._currentImage = value

    @property
    def images(self):
        return self._images
    
    @property
    def image(self):
        return self.images[self.currentImage]

    @property
    def width(self):
        return self.image.get_width()

    @property
    def height(self):
        return self.image.get_height()
    
    def update(self):
        pass

    def draw(self, screen):
        rx = self.width / 2
        ry = self.height / 2
        pos = (self._pos[0] - rx, self._pos[1] - ry)
        screen.blit(self.image, list(pos))
        
    def set_left(self, value):
        self._pos[0] = value

    def set_top(self, value):
        self._pos[1] = value
        
    def set_pos(self, value):
        self._pos = value

    def left(self):
        return self._pos[0]
    
    def pos(self):
        return self._pos

    def top(self):
        return self._pos[1]
