import sys
import os

basedir = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(basedir, "common"))

from xrandr import XRandr
import logging

class Brightness:
    def __init__(self, dimValue, lightValue):
        logging.debug(f"{self.__class__.__name__}.__init__(dimValue={dimValue}, lightValue={lightValue})")
        self._xrandr = XRandr()
        self._output = self._xrandr.getOutput()
        self._dimValue = dimValue
        self._lightValue = lightValue
        self._currentValue = self._xrandr.getBrightness(self._output)
        
    def dimValue(self):
        return self._dimValue
        
    def lightValue(self):
        return self._lightValue
        
    def setCurrentValue(self, value):
        self._currentValue = value
        self._xrandr.setBrightness(self._output, self._currentValue)
        
    def setDimValue(self, value):
        if self._currentValue == self._dimValue:
            self.setCurrentValue(value)
        self._dimValue = value
        
    def setLightValue(self, value):
        if self._currentValue == self._lightValue:
            self.setCurrentValue(value)
        self._lightValue = value
        
    def toggle(self):
        newValue = self._dimValue if self._currentValue == self._lightValue else self._lightValue
        logging.debug(f"Brightness.toggle(currentValue={self._currentValue}, newValue={newValue})")
        self.setCurrentValue(newValue)

    def dim(self):
        self.setCurrentValue(self._dimValue)

    def light(self):
        self.setCurrentValue(self._lightValue)

if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.DEBUG)
    
    brightness = Brightness(0.2, 1.0)
    
    brightness.toggle()
    time.sleep(3)
    brightness.toggle()
