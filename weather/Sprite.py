import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..', 'common'))
from FileSelector import FileSelector
import pygame

class Sprite:
    FileSelector = FileSelector(os.path.join(os.getcwd(), 'images'), ['png', 'jpg', 'svc'])
    def __init__(self, imagename, pos = (0, 0), size = None):
        imagepath = Sprite.FileSelector.select(imagename)
        image = pygame.image.load(imagepath)
        if size == None:
            self._image = image
        else:
            self._image = pygame.transform.scale(image, size)
        self._pos = pos
        self._size = size
        pass

    def update(self):
        pass

    def draw(self, screen):
        rx = self._image.get_width() / 2
        ry = self._image.get_height() / 2
        pos = (self._pos[0] - rx, self._pos[1] - ry)
        screen.blit(self._image, list(pos))
        
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
