from pgrunner import *
from graphs import *

class Button(GraphObject):
    def __init__(self, name, text, pos: Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, pos = pos, size = size, orientation = orientation, parent = parent)
        logging.debug(f"{self.__class__.__name__}.__init__(kwargs={kwargs})")
        self._text = text
        self._border = 3 if not "border" in kwargs else int(kwargs["border"])
        self._fgColor = Colors.Black if not "fgColor" in kwargs else kwargs["fgColor"]
        self._bgColor = Colors.LightGray if not "bgColor" in kwargs else kwargs["bgColor"]
        self._font = Fonts.Arial12 if not "font" in kwargs else kwargs["font"]
        logging.debug(f"{self.__class__.__name__}.__init__(font={self._font}, bgColor={self.bgColor})")
        self._sunken = False
        self._sunkenSurface = None
        self._raisedSurface = None

    def __str__(self):
        return (super().__str__() +
                f", border={self.border}" +
                f", bgColor={self.bgColor}, fgColor={self.fgColor}, font={self.font}")

    def __repr__(self):
        return "Button(" + self.__str__() + ")"
    
    @property
    def sunken(self):
        return self._sunken

    @sunken.setter
    def sunken(self, value):
        self._sunken = value
        
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        self._border = value

    @property
    def bgColor(self):
        return self._bgColor

    @bgColor.setter
    def bgColor(self, value):
        self._bgColor = value

    @property
    def fgColor(self):
        return self._fgColor

    @fgColor.setter
    def fgColor(self, value):
        self._fgColor = value

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value

    def onMouseDown(self, pos, button, obj):
        self._sunken = True
        return False

    def onMouseUp(self, pos, button, obj):
        self._sunken = False
        return False

    def createSurface(self):
        raise NotImplemented(f"createSurface is not implemented in {self.__class__.__name__}")

    def getText(self):
        buttonText = self.font.render(self.text, True, self.fgColor)
        x = (self.size.width - buttonText.get_width())/2+(self.border/2 if self.sunken else 0)
        y = (self.size.height - buttonText.get_height())/2 + (self.border/2 if self.sunken else 0)
        return buttonText, x, y

    def draw(self, screen):
        if self._sunkenSurface == None or self._raisedSurface == None:
            self.createSurface()
            
        surface = self._sunkenSurface if self.sunken else self._raisedSurface

        if surface == None or not isinstance(surface, PGSurface):
            raise RuntimeError("Surface is not defined!")

        super().paint(screen, surface._surface)
        
class Border3DButton(Button):
    def __init__(self, name, text, pos: Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, text=text, pos=pos, size=size, orientation=orientation, parent=parent, **kwargs)
        logging.debug(f"{self.__class__.__name__}.__init__(font={self.font})")
        self._borderColor = kwargs["borderColor"] if "borderColor" in kwargs else self.fgColor
        logging.debug(f"{self.__class__.__name__}.__init__(font={self.font})")
        self._surface = PGSurface(size, alpha=255)
        logging.debug(f"{self.__class__.__name__}.__init__({self.__str__})")
        self._sunkenSurface = None
        self._raisedSurface = None

    def __str__(self):
        return super().__str__() + f", borderColor={self.borderColor}"

    def __repr__(self):
        return "Border3DButton(" + self.__str__() + ")"
    
    @property
    def borderColor(self):
        return self._borderColor

    @borderColor.setter
    def borderColor(self, value):
        self._borderColor = value

    def createSurface(self):
        rectSurf = PGSurface(self.size, alpha=0)
        rectSurf.drawBorder(self.border, self.bgColor, self.borderColor, self.sunken)
        buttonText, x, y = self.getText()
        textPos = (x, y)
        rectSurf._surface.blit(buttonText, textPos)
        if self.sunken:
            self._sunkenSurface = rectSurf
        else:
            self._raisedSurface = rectSurf
        

class FlatButton(Button):
    def __init__(self, name, text, pos : Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, text=text, pos=pos, size=size, orientation=orientation, parent = parent, **kwargs)

    def createSurface(self):
        if self._sunkenSurface == None and self.sunken: 
            surface = PGSurface(self.size + Size((self.border,self.border)), alpha=0)
            surface.fill(Colors.Black)
            surface.drawRect(Rect(Point((self.border, self.border)), self.size), self.bgColor)
            textSurface, x, y = self.getText()
            surface._surface.blit(textSurface, (x,y))
            self._sunkenSurface = surface
        elif self._raisedSurface == None and not self.sunken:
            surface = PGSurface(self.size + Size((self.border,self.border)), alpha=0)
            surface.fill(Colors.Black)
            surface.drawRect(Rect(Point((self.border, self.border)), self.size), Colors.Black + (255,))
            surface.drawRect(Rect(Point((0,0)), self.size), self.bgColor)
            textSurface, x, y = self.getText()
            surface._surface.blit(textSurface, (x,y))
            self._raisedSurface = surface
            
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = PGRunner("main", Size((1024,768)), Colors.White)
        button1 = Border3DButton(name="button1",text="Button", pos=Point((10, 10)), size=Size((120, 50)), parent = runner, fgColor=Colors.Black, bgColor = Colors.LightGray, borderColor = Colors.Black, border=3)
        button2 = FlatButton(name="button2", text="Button", pos=Point((140, 10)), size=Size((120, 50)), parent=runner, fgColor=Colors.Black, bgColor=Colors.LightBlue, border=5)
        group = GraphObjectGroup(name="group1", pos = Point((0, 0)), size = Size((1024, 768)), backgroundColor=Colors.White)
        logging.debug(f"button1={repr(button1)}, button2={repr(button2)}")
        group.addGraphObject(button1)
        group.addGraphObject(button2)
        runner.addGraphObject(group)
        runner.run()
    except Exception as e:
        logging.exception(e)
    finally:
        pygame.quit()
        sys.exit()
                            
        

