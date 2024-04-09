import sys
import os

basedir = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(basedir, "pgrunner"))

from pgrunner import PGRunner, Colors, Orientation, Fonts, Text
import logging
import pygame

from time import strftime, localtime
from Clock import Clock

class Radio(PGRunner):

    def __init__(self):
        super().__init__(800, 400, Colors.Black)
        self.addGraphObject(Clock(size=(800, 400), pos = (0, 0)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = Radio()
        runner.run()
    except Exception as e:
        logging.exception(e)
    finally:
        pygame.quit()
        sys.exit()
