from pgrunner import *
from graphs import *

class Button(GraphObject):
    def __init__(self, name, text, pos: Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, pos = pos, size = size, orientation = orientation, parent = parent)
        self._text = text
        self._border = 3 if not "border" in kwargs else int(kwargs["border"])
        self._fgColor = Colors.Black if not "fgColor" in kwargs else kwargs["fgColor"]
        self._bgColor = Colors.LightGray if not "bgColor" in kwargs else kwargs["bgColor"]
        self._font = Fonts.Arial12 if not "font" in kwargs else kwargs["font"]
        self._pressed = False
        self._pressedSurface = None
        self._releasedSurface = None

    def __str__(self):
        return (super().__str__() +
                f", border={self.border}" +
                f", bgColor={self.bgColor}, fgColor={self.fgColor}, font={self.font}")

    def __repr__(self):
        return "Button(" + self.__str__() + ")"
    
    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def sunken(self, value):
        self._pressed = value
        
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
        self._pressed = True
        return False

    def onMouseUp(self, pos, button, obj):
        self._pressed = False
        return False

    def createPressedSurface(self):
        raise NotImplementedError(f"{self.__class__.__name__}.createSunkenSurface is not implemented yet!")
    
    def createReleasedSurface(self):
        raise NotImplementedError(f"{self.__class__.__name__}.createRaisedSurface is not implemented yet!")

    def create(self):
        self._pressedSurface = self.createPressedSurface()
        self._releasedSurface = self.createReleasedSurface()

    def getText(self, pressed):
        buttonText = self.font.render(self.text, True, self.fgColor)
        x = (self.size.width - buttonText.get_width())/2+(self.border if pressed else 0)
        y = (self.size.height - buttonText.get_height())/2 + (self.border if pressed else 0)
        return buttonText, x, y

    def draw(self, screen):
        if self._pressedSurface == None:
            raise RuntimeError(f"Pressed Surface is not created in {self.__class__.__name__}!")
        if self._releasedSurface == None:
            raise RuntimeError(f"Released Surface is not created in {self.__class__.__name__}!")
        
        surface = self._pressedSurface if self.pressed else self._releasedSurface

        if surface == None or not isinstance(surface, PGSurface):
            raise RuntimeError("Surface is not defined!")

        super().paint(screen, surface._surface)
        
class Border3DButton(Button):
    def __init__(self, name, text, pos: Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, text=text, pos=pos, size=size, orientation=orientation, parent=parent, **kwargs)
        self._borderColor = kwargs["borderColor"] if "borderColor" in kwargs else self.fgColor

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

    def createSurface(self, pressed):
        self.debug("()")
        surface = PGSurface(self.size, alpha=0)
        surface.drawBorder(self.border, self.bgColor, self.borderColor, pressed)
        buttonText, x, y = self.getText(pressed)
        textPos = (x, y)
        surface._surface.blit(buttonText, textPos)
        return surface

    def createPressedSurface(self):
        return self.createSurface(True)
    
    def createReleasedSurface(self):
        return self.createSurface(False)

class FlatButton(Button):
    def __init__(self, name, text, pos : Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, text=text, pos=pos, size=size, orientation=orientation, parent = parent, **kwargs)

    def createPressedSurface(self):
        surface = PGSurface(self.size + Size((self.border,self.border)), alpha=0)
        surface.fill(Colors.Black)
        surface.drawRect(Rect(Point((self.border, self.border)), self.size), self.bgColor)
        textSurface, x, y = self.getText(True)
        surface._surface.blit(textSurface, (x, y))
        return surface

    def createReleasedSurface(self):
        surface = PGSurface(self.size + Size((self.border,self.border)), alpha=0)
        surface.fill(Colors.Black)
        surface.drawRect(Rect(Point((self.border, self.border)), self.size), Colors.Black + (255,))
        surface.drawRect(Rect(Point((0,0)), self.size), self.bgColor)
        textSurface, x, y = self.getText(False)
        surface._surface.blit(textSurface, (x,y))
        return surface

class ImageButton(Button):
    def __init__(self, name, pos : Point, size : Size, orientation = Orientation.TopLeft, parent = None, **kwargs):
        super().__init__(name, text="", pos=pos, size=size, orientation=orientation, parent=parent, **kwargs)
        if not "releasedImage" in kwargs:
            raise AttributeError("Param \"releasedImage\" is not defined!")
        if not "pressedImage" in kwargs:
            raise AttributeError("Param \"pressedImage\" is not defined!")
        self._releasedImage = kwargs["releasedImage"]
        self._pressedImage = kwargs["pressedImage"]

    def createPressedSurface(self):
        image = PGImage(self.size, self._pressedImage)
        return image._surface

    def createReleasedSurface(self):
        image = PGImage(self.size, self._releasedImage)
        return image._surface
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        PGRunner.Ticks = 16
        runner = PGRunner("main", Size((1024,768)), Colors.White)
        button1 = Border3DButton(name="button1",text="Button", pos=Point((10, 10)), size=Size((120, 50)), parent = runner, fgColor=Colors.Black, bgColor = Colors.LightGray, borderColor = Colors.Black, border=3)
        button2 = FlatButton(name="button2", text="Button", pos=Point((140, 10)), size=Size((120, 50)), parent=runner, fgColor=Colors.Black, bgColor=Colors.LightBlue, border=5)
        group = GraphObjectGroup(name="group1", pos = Point((0, 0)), size = Size((1024, 768)), backgroundColor=Colors.White)
        group.addGraphObject(button1)
        group.addGraphObject(button2)
        runner.addGraphObject(group)
        runner.run()
    except Exception as e:
        logging.exception(e)
    finally:
        pygame.quit()
        sys.exit()
                            
        

