import pygame
from astral.sun import elevation, azimuth
import math
from datetime import timedelta
import astraltimes
from area import Area
from astral import LocationInfo
from astral.moon import moonrise, moonset, phase
from astral.sun import sun, daylight
from astral.location import Location
from datetime import datetime, timedelta
import logging
import sys
import os
from FontFactory import FontFactory
from Sprite import Sprite
from Sattelite import Sattelite

pygame.init()

logging.basicConfig(level=logging.DEBUG)

WIDTH=1024
HEIGHT=768

class Colors:
    Black = (0, 0, 0)
    White = (255, 255, 255)
    Blue = (0, 0, 255)
    LightBlue = (173, 216, 230)
    LightGray = (192, 192, 192)

class Program:
    BackgroundColor = Colors.LightBlue
    TextColor = Colors.Black
    
    def __init__(self):
        logging.debug(f"{self.__class__.__name__}.__init__()")
        today = datetime.today()
        self.timedelta = timedelta(minutes=1)
        spriteSize = (64,64)
        self.sattelite = Sattelite(spriteSize, (WIDTH, HEIGHT))
        self.dt = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=self.sattelite.tzInfo)
        self.sattelite.dt = self.dt
        self.sattelite.currentDay = self.dt.day
        self.clock = pygame.time.Clock()
        self.running = True
        self.rotation = True
        FontFactory.FontDefinitionPath = "./fonts.json"
        self._fontFactory = FontFactory.Get()
        self._font = 'arial14'
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    @property
    def font(self):
        return self._fontFactory[self._font]
    
    def update(self):
        if self.rotation:
            self.dt = self.dt + self.timedelta
        self.sattelite.dt = self.dt
        self.sattelite.update()
        self.caption = self.sattelite.timeStr
        
    def draw(self):
        self.screen.fill(Program.BackgroundColor)
        x, y = (50, 30)
        for line in self.caption.split('#'):            
            text = self.font.render(line, True, Program.TextColor)
            self.screen.blit(text, [x, y])
            y += text.get_height()
        self.sattelite.draw(self.screen)

    def onMouseDown(self, pos, button):
        self.rotation = not self.rotation

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.onMouseDown(event.pos, event.button)
                
    def run(self):
        while self.running:
            self.handleEvents()
            self.update()
            self.draw()
            self.clock.tick(60)
            pygame.display.flip()
        pygame.quit()
        
logging.basicConfig(level=logging.DEBUG)
program = Program()
program.run()
sys.exit()

    

