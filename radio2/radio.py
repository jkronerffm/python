import sys
import os

basedir = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(basedir, "pgrunner"))

from pgrunner import PGRunner, Colors, Orientation, Fonts, Text
from time import strftime, localtime
import logging
import pygame

class Radio(PGRunner):

    def __init__(self):
        super().__init__(800, 400, Colors.Black)
        self.addGraphObject(Clock())
        self.addGraphObject(Date())
        
class Clock(Text):
    def __init__(self):
        super().__init__("", pos=(400, 200),font = Fonts.Arial64, orientation = Orientation.BottomCenter)

    def update(self):
        now = localtime()
        time = strftime("%H:%M", now)
        self._text = time

    def draw(self, screen):
        super().draw(screen)

class Date(Text):
    def __init__(self):
        super().__init__("", pos=(400, 200), font = Fonts.Arial18, orientation = Orientation.TopCenter)

    def update(self):
        now = localtime()
        date = strftime("%d.%m.%Y", now)
        self._text = date

    def draw(self, screen):
        super().draw(screen)
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = Radio()
        runner.run()
    except Exception as e:
        print(e)
    finally:
        pygame.quit()
        sys.exit()
