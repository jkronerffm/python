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
        self.area = Area("Frankfurt am Main", "Germany", "Europe/Berlin", 50.11, 8.68)
        locationInfo = LocationInfo(self.area.city(), self.area.country(), self.area.timezone(), self.area.latitude(), self.area.longitude())
        location = Location(locationInfo)
        tzinfo = locationInfo.tzinfo
        self.observer = location.observer
        today = datetime.today()
        self.dt = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=tzinfo)
        self.timedelta = timedelta(minutes=1)
        self.origin = (WIDTH/2, HEIGHT/2)
        self.dx = float(WIDTH) / 2.0 - 32
        self.dy = float(HEIGHT) / 2.0 - 32
        spriteSize = (64,64)
        self.sun = Sprite('sun2', size=spriteSize)
        self.redSun = Sprite('redsun', size=spriteSize)
        self.moon = Sprite('moon2', size=spriteSize)
        self.sunValues = sun(self.observer, today)
        self.clock = pygame.time.Clock()
        self.running = True
        FontFactory.FontDefinitionPath = "./fonts.json"
        self._fontFactory = FontFactory.Get()
        self._font = 'arial14'
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    @property
    def font(self):
        return self._fontFactory[self._font]
    
    def update(self):
        el = elevation(self.observer, self.dt)
        az = azimuth(self.observer, self.dt)
        elr = math.radians(el)
        azr = math.radians(90.0 - az)
        x = self.origin[0] - math.cos(azr) * self.dx
        y = self.origin[1] - math.sin(elr) * self.dy
        if self.dt < self.sunValues['dawn'] or self.dt > self.sunValues['dusk']:
            self.sattelite = self.moon
        elif self.dt >= self.sunValues['dawn'] and self.dt < self.sunValues['sunrise']:
            self.sattelite = self.redSun
        elif self.dt >= self.sunValues['sunrise'] and self.dt < self.sunValues['sunset']:
            self.sattelite = self.sun
        else:
            self.sattelite = self.redSun
        self.sattelite.set_pos((x,y))
        day = self.dt.day
        self.dt = self.dt + self.timedelta
        if self.dt.day != day:
            self.sunValues= sun(self.observer, self.dt.date())
        timestr = self.dt.strftime("%d.%m.%Y %H:%M")
        dawnstr = self.sunValues['dawn'].strftime("%d.%m.%Y %H:%M")
        duskstr = self.sunValues['dusk'].strftime("%d.%m.%Y %H:%M")
        self.caption = "time=%s#dawn=%s#dusk=%s#time<dawn: %s#time>dusk: %s#elevation=%.2f#azimuth=%.2f#(x=%d, y=%d)" % (timestr,dawnstr, duskstr,self.dt< self.sunValues['dawn'], self.dt > self.sunValues['dusk'],el, az, x, y)
        
    def draw(self):
        self.screen.fill(Program.BackgroundColor)
        x, y = (50, 30)
        for line in self.caption.split('#'):            
            text = self.font.render(line, True, Program.TextColor)
            self.screen.blit(text, [x, y])
            y += text.get_height()
        self.sattelite.draw(self.screen)

    def onMouseDown(self, pos, button):
        self.running = False

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

    

