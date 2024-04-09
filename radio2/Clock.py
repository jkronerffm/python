import sys
import os

basedir = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(basedir, "pgrunner"))

from pgrunner import PGRunner, Colors, Orientation, Fonts, Text, GraphObjectGroup
import logging
import pygame
from time import localtime, strftime

class Time(Text):
    def __init__(self):
        super().__init__("", pos=(400, 200),font = Fonts.Arial128, orientation = Orientation.BottomCenter)

    def update(self):
        now = localtime()
        time = strftime("%H:%M", now)
        self._text = time

    def draw(self, surface):
#        logging.debug(f"Time.draw(surface={surface})")
        super().draw(surface)

class Date(Text):
    def __init__(self):
        super().__init__("", pos=(400, 200), font = Fonts.Arial64, orientation = Orientation.TopCenter)

    def update(self):
        now = localtime()
        date = strftime("%d.%m.%Y", now)
        self._text = date

    def draw(self, surface):
#        logging.debug(f"Date.draw(surface={surface})")
        super().draw(surface)

class Clock(GraphObjectGroup):
    def __init__(self, size=(800, 400), pos = (0,0), orientation = Orientation.TopLeft, active=True):
        logging.debug(f"Clock.__init__(size={size}, pos={pos})")
        super().__init__(pos=pos, size=size, orientation=orientation, backgroundColor = Colors.Black, active = active)
        self.addGraphObject(Time())
        self.addGraphObject(Date())
