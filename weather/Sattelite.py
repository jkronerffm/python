from Sprite import Sprite
from datetime import timedelta
import astraltimes
from area import Area
from astral import LocationInfo
from astral.moon import moonrise, moonset, phase
from astral.sun import sun, daylight
from astral.location import Location
from astral.sun import elevation, azimuth
import math
from datetime import datetime, timedelta

class Sattelite:
    Moon = 'moon4'
    Sun = 'sun2'
    Redsun = 'redsun4'
    
    def __init__(self, size, screenSize):
        self._size = size
        self._screenSize = screenSize
        self.area = Area("Frankfurt am Main", "Germany", "Europe/Berlin", 50.11, 8.68)
        self._locationInfo = LocationInfo(self.area.city(), self.area.country(), self.area.timezone(), self.area.latitude(), self.area.longitude())
        self.location = Location(self.locationInfo)
        self.tzinfo = self.locationInfo.tzinfo
        self.observer = self.location.observer
        self._dt = None
        self.currentDay = None
        self._origin = (self.screenWidth/2, self.screenHeight/2)
        self._delta = (float(self.screenWidth - self.spriteWidth) / 2.0, float(self.screenHeight - self.spriteHeight) / 2.0)
        self.sattelite = Sprite((Sattelite.Sun, Sattelite.Redsun, Sattelite.Moon), size=self._size)
        self.sunValues = sun(self.observer, datetime.today())
        self.maxAzimuth = 0
        self.maxElevation = 0

    @property
    def tzInfo(self):
        return self.tzinfo
    
    @property
    def locationInfo(self):
        return self._locationInfo
    
    @property
    def dx(self):
        return self._delta[0]

    @property
    def dy(self):
        return self._delta[1]
    
    @property
    def originX(self):
        return self._origin[0]

    @property
    def originY(self):
        return self._origin[1]

    @property
    def screenWidth(self):
        return self._screenSize[0]

    @property
    def screenHeight(self):
        return self._screenSize[1]

    @property
    def spriteWidth(self):
        return self._size[0]

    @property
    def spriteHeight(self):
        return self._size[1]
    
    @property
    def dt(self):
        return self._dt

    @dt.setter
    def dt(self, value):
        self._dt = value

    @property
    def currentDay(self):
        return self._currentDay

    @currentDay.setter
    def currentDay(self, value):
        self._currentDay = value

    @property   
    def timeStr(self):
        timestr = self.dt.strftime("%d.%m.%Y %H:%M")
        dawnstr = self.sunValues['dawn'].strftime("%d.%m.%Y %H:%M")
        duskstr = self.sunValues['dusk'].strftime("%d.%m.%Y %H:%M")
        timeStr = "time=%s#dawn=%s#dusk=%s#time<dawn: %s#time>dusk: %s#elevation=%.2f (max=%.2f)#azimuth=%.2f (max=%.2f)#(x=%d, y=%d)" % (timestr,dawnstr, duskstr,self.dt< self.sunValues['dawn'], self.dt > self.sunValues['dusk'],self.el, self.maxElevation, self.az, self.maxAzimuth, self.x, self.y)
        return timeStr

    @property
    def pos(self):
        return (self.x, self.y)

    @pos.setter
    def pos(self, value):
        self.x = value[0]
        self.y = value[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def update(self):
        if self.dt.day != self.currentDay:
            self.sunValues = sun(self.observer, self.dt.date())
            self.currentDay = self.dt
            
        self.el = elevation(self.observer, self.dt)
        self.az = azimuth(self.observer, self.dt)
        if self.az > self.maxAzimuth:
            self.maxAzimuth = self.az
        if self.el > self.maxElevation:
            self.maxElevation = self.el
        elr = math.radians(self.el)
        azr = math.radians(90-self.az)
        self.x = self.originX - math.cos(azr) * self.dx
        self.y = self.originY - math.sin(elr) * self.dy
        if self.dt < self.sunValues['dawn'] or self.dt > self.sunValues['dusk']:
            self.sattelite.currentImage = Sattelite.Moon
        elif self.dt >= self.sunValues['dawn'] and self.dt < self.sunValues['sunrise']:
            self.sattelite.currentImage = Sattelite.Redsun
        elif self.dt >= self.sunValues['sunrise'] and self.dt < self.sunValues['sunset']:
            self.sattelite.currentImage = Sattelite.Sun
        else:
            self.sattelite.currentImage = Sattelite.Redsun
        self.sattelite.set_pos(self.pos)

    def draw(self, screen):
        self.sattelite.draw(screen)
        
