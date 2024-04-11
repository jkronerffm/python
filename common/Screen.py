from xrandr import XRandr
from XSet import XSet
import logging

class Screen:
    """
    The class Screen supports some functions on Screen.

    Attributes
    ----------
    _xrandr : XRandr
        calls some functions on command xrandr
    _xset : XSet
        calls some functions on command xset
    _name : str
        the name of connected display returned from xrandr
    _dimValue : float
        the brightness value of dimmed screen.
    _currentValue : float
        the current value of brightness
    _lightValue : float
        the brightness value of lighted screen.
    _on : the current on-/off-state of screen
    
    """
    
    def __init__(self):
        """
        Initializes the Screen object. To perform functions on Screen it
        generates objects of type XRandr and XSet. To perform operations
        on XRandr it gets the name as output from XRandr. To perform on
        XSet it gets the display from environment variable $DISPLAY

        Initializes the object variables.
        """
        
        logging.debug(f"{self.__class__.__name__}.__init__()")
        self._xrandr = XRandr()
        self._xset = XSet()
        self._name = self._xrandr.getOutput()
        self._dimValue = 0.2
        self._lightValue = 1.0
        self._on = True
        self._currentValue = self._xrandr.getBrightness(self._name)

    def name(self):
        """
        Returns the name of xrandr output
        """
        
        return self._name
    
    def dimValue(self):
        """
        Returns the value of dimmed brightness
        """
        
        return self._dimValue
        
    def lightValue(self):
        """Returns the value of lighted brightness"""
        
        return self._lightValue
        
    def setCurrentValue(self, value):
        """Sets current value of brightness. Sets the brightness of screen via xrandr."""
        
        self._currentValue = value
        self._xrandr.setBrightness(self._name, self._currentValue)
        
    def setDimValue(self, value):
        """
        Sets the value of dimmed brightness.

        If currenly screen is dimmed the new value will be activated immediately.
        """
        
        if self._currentValue == self._dimValue:
            self.setCurrentValue(value)
        self._dimValue = value
        
    def setLightValue(self, value):
        """
        Sets the value of lighted brightness.

        If currenly screen is lighted the new value will be activated immediately.
        """
        
        if self._currentValue == self._lightValue:
            self.setCurrentValue(value)
        self._lightValue = value
        
    def toggleBrightness(self):
        """
        Toggles the brightness.
        """
        
        newValue = self._dimValue if self._currentValue == self._lightValue else self._lightValue
        logging.debug(f"Brightness.toggle(currentValue={self._currentValue}, newValue={newValue})")
        self.setCurrentValue(newValue)

    def isOn(self):
        """
        Returns if screen is currently switched on.
        """
        
        return self._on
    
    def toggle(self):
        """
        Toggles the screen between on and off
        """
        
        toggleTo = not self.isOn()
        self._xset.toggle(toggleTo)
        self._on = toggleTo
        return self.isOn()

    def on(self):
        """
        Turns on the screen
        """

        self._xset.on()

    def off(self):
        """
        Turns off the screen.
        """

        self._xset.off()
        
    def dim(self):
        """
        Dims the screen.
        """
        self.setCurrentValue(self._dimValue)

    def light(self):
        """
        Lightens the screen.
        """
        
        self.setCurrentValue(self._lightValue)

if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.DEBUG)
    
    screen = Screen()

    for task in [lambda s: s.toggleBrightness(),
                 lambda s: s.toggleBrightness(),
                 lambda s: s.toggle(),
                 lambda s: s.toggle()]:
        task(screen)
        time.sleep(3)
