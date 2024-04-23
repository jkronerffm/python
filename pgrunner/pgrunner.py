import pygame
import sys
import os
import logging
from graphs import *
import inspect

pygame.init()

class Colors:
    Black = (0, 0, 0)
    White = (255, 255, 255)
    Blue = (0, 0, 255)
    LightBlue = (173, 216, 230)
    LightGray = (192, 192, 192)

class Fonts:
    Arial12 = pygame.font.SysFont('Arial', 12, False, False)
    Arial14 = pygame.font.SysFont('Arial', 14, True, False)
    Arial18 = pygame.font.SysFont('Arial', 18, True, False)
    Arial64 = pygame.font.SysFont('Arial', 64, True, False)
    Arial128 = pygame.font.SysFont('Arial', 128, True, False)

class Orientation:
    Top = 1
    Bottom = 2
    VCenter = 3
    Left = 16
    Right = 32
    HCenter = 48
    TopLeft = 17
    TopRight = 33
    BottomLeft = 18
    BottomRight = 34
    TopCenter = 49
    BottomCenter = 50
    LeftCenter = 19
    RightCenter = 35
    Center = 51

class EventHandler:
    '''
    The class EventHandler maps the event by type to a function by name.

    Attributes:
        Map:   The map from event.type to function by name.
    '''
    Map = {
        pygame.MOUSEBUTTONDOWN: 'onMouseDown',
        pygame.MOUSEBUTTONUP: 'onMouseUp',
        pygame.MOUSEMOTION: 'onMouseMove',
        pygame.QUIT: 'onQuit'
    }

    @classmethod
    def MapEvent(cls, event, obj):
        '''
        MapEvent maps the event to a method of obj.

        :param cls:   The EventHandler class.
        :param event: The event object to map to function in obj.
        :param obj:   The object that contains method the event is to be mapped to.
        :return:      The return value of method called in obj.

        The event is mapped by attr type to obj. The mapping from event.type to method name is described
        in class member Map. Params of method must be found by name in event.
        '''
        funcName = EventHandler.Map[event.type] if event.type in EventHandler.Map.keys() else None
        func = getattr(obj, funcName) if funcName != None and hasattr(obj, funcName) else None
        if func == None:
            return None
        argSpec = inspect.getfullargspec(func)
        params = []
        for arg in argSpec.args:
            if arg == "self":
                continue
            if hasattr(event,arg):
                val = getattr(event, arg)
                params.append(val)
        result = func(*params)
        return result
    
class GraphBase:
    '''
    GraphBase is Base class for all objects. It defines a method debug for common debugging
    '''
    def debug(self, msg, **kwargs):
        '''
        The method writes a debug message.

        :param self:   The pointer to the object itself.
        :param msg:    The msg to be written to debug output.
        :param kwargs: The keyword args.

        Expected keys in kwargs:
            classname: The name of class to be written in output. If not given,
            self.__class__.__name__ will be used
            condition: The condition to write out the msg. If not given, it will be written.

graphs.py
        '''
        classname = kwargs['classname'] if 'classname' in kwargs else self.__class__.__name__
        condition = kwargs['condition'] if 'condition' in kwargs else True
        if condition:
            logging.debug(f"{classname}.{inspect.stack()[1][3]}{msg}")
            
class PGSurface(GraphBase):
    
    def __init__(self, size : Size, **kwargs):
        self._size = size
        self._alpha = kwargs['alpha'] if 'alpha' in kwargs.keys() else 255
        self._surface = self.getSurface()
        self.debug(f"PGSCreen(screen={self._surface}, size={self.size()})")

    def getSurface(self):
        if self._alpha < 255:
            return pygame.Surface(self.size(), pygame.SRCALPHA)
        else:
            return pygame.Surface(self.size())
    
    def fill(self, color):
        colorValue = color
        if self._alpha < 255:
            colorValue += (self._alpha,)
        self._surface.fill(colorValue)

    def drawText(self, text, fgColor, font):
        surface = font.render(text, True, fgColor)
        return surface

    def drawImage(self, image, pos):
        self._surface.blit(image, pos)

    def drawRect(self, rect : Rect, color, width = 0):
        pygame.draw.rect(self._surface, color, tuple(rect.pos) + tuple(rect.size), width)
        
    def paint(self, surface, pos):
        self._surface.blit(surface, pos)

    def size(self):
        return tuple(self._size)

    def surface(self):
        return self._surface
    
class PGScreen(PGSurface):
    def __init__(self, size : Size):
        super().__init__(size)

    def getSurface(self):
        return pygame.display.set_mode(self.size())

class PGImage(PGSurface):
    def __init__(self, size: Size, filepath : str):
        self.debug(f"(size={Size}, filepath={filepath})")
        if len(filepath) > 0:
            image = pygame.image.load(filepath)
            self.debug(f"(image={image})")
            rel = image.get_width() / image.get_height()
            self.debug(f"() => rel of image size = {rel}")
            newHeight = int(size.width / rel)
            if newHeight < size.height:
                newWidth = int(size.height * rel)
                newSize = Size((newWidth, size.height))
            else:
                newSize = Size((size.width, newHeight))
            self.debug(f"() => transform.scale({image}, {(size.width, newHeight)})")
            imageScaled = pygame.transform.scale(image, tuple(newSize))
            self._image = pygame.Surface(tuple(size))
            self._image.blit(imageScaled, (0, 0) + tuple(size))
            self.debug(f"(image={self._image})")

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        
class GraphObject(GraphBase):
    def __init__(self, pos : Point((0, 0)), size : Size = None, orientation = Orientation.TopLeft, active = True, parent=None):
        self._pos = pos
        self._parent = parent
        self._size = size
        self._orientation = orientation
        self._active = active
        self.debug(f"(pos={self._pos}, size={self._size})", classname="GraphObject")

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        
    def isIn(self, pos : Point):
        return Rect(self._pos, self._size).contains(pos)
        
    def isActive(self):
        return self._active
    
    def update(self):
        pass
    
    def draw(self, screen):
        pass            

    def onMouseDown(self, pos, button):
        return False

    def onMouseUp(self, pos, button):
        return False

    def onMouseMove(self, pos):
        return False
        
    def eventHandler(self, event):
        localPos = self.parent.rect().surfaceToRect(Point(event.pos)) if self.parent != None else Point(event.pos)
        result = False
        result = EventHandler.MapEvent(event, self)

        return result
        
    def _getPosAtOrientation(self):
        if (self._orientation & Orientation.HCenter) == Orientation.HCenter:
            x = self._pos.x - self.width / 2
        elif (self._orientation & Orientation.Left) == Orientation.Left:
            x = self._pos.x
        elif (self._orientation & Orientation.Right) == Orientation.Right:
            x = self._pos.x - self.width
        else:
            x = self._pos.x
        if (self._orientation & Orientation.VCenter) == Orientation.VCenter:
            y = self._pos.y - self.height/2
        elif (self._orientation & Orientation.Top) == Orientation.Top:
            y = self._pos.y
        elif (self._orientation & Orientation.Bottom) == Orientation.Bottom:
            y = self._pos.y - self.height
        else:
            y = self._pos.y

        return x, y
        
    def paint(self, screen, surface):
        width = surface.get_width()
        height = surface.get_height()
        self._size = Size((width, height))
        x, y = self._getPosAtOrientation()
        screen.paint(surface, [x, y])

    @property        
    def pos(self):
        return self._pos

    @pos.setter
    def setPos(self, pos):
        self._pos = pos

    @property
    def left(self):
        return self._pos.x

    @property
    def top(self):
        return self._pos.y

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size : Size):
        self._size = size

    @property
    def width(self):
        return self._size.width if self._size != None else 0

    @width.setter
    def width(self, value):
        if self.size == None:
            self.size = Size(value, 0)
        else:
            self.size.width = value
            
    @property
    def height(self):
        return self._size.height if self._size != None else 0

    @height.setter
    def height(self,  value):
        if self.size == None:
            self.size = Size(0, value)
        else:
            self.size.height = value
            
    def rect(self):
        x,y = self._getPosAtOrientation()
        return Rect(Point((x,y)), self._size)

    def surfaceToRect(self, point : Point):
        myPoint = point if self.parent == None else self.parent.surfaceToRect(point)
        return self.rect().surfaceToRect(myPoint)
            
class GraphObjectGroup(GraphObject):

    def __init__(self, size : Size, pos = Point((0,0)), orientation = Orientation.TopLeft, backgroundColor = Colors.Black, alpha=255, active=True, parent = None):
        super().__init__(pos, size, orientation, active=active, parent = parent)
        self.debug(f"(pos={self._pos}, size={self._size}, orientation={orientation}, backgroundColor={backgroundColor}, alpha={alpha})",classname="GraphObjectGroup")
        self._backgroundColor = backgroundColor
        self._graphObjects = []
        self._surface = PGSurface(self.size, alpha = alpha)
        
    def addGraphObject(self, graphObject):
        self._graphObjects.append(graphObject)
        graphObject.parent = self

    def draw(self, screen):
        if not self.isActive():
            return
        
        self._surface.fill(self._backgroundColor)
        for graphObject in self._graphObjects:
            graphObject.draw(self._surface)
        super().paint(screen, self._surface.surface())

    def eventHandler(self, event):
        handled = False
        localPos = self.surfaceToRect(Point(event.pos))
        for graphObject in self._graphObjects:
            if graphObject.size == None:
                continue
            if graphObject.rect().contains(localPos):
                handled = graphObject.eventHandler(event)
            if handled:
                break

        if not handled:
            handled = super().eventHandler(event)
            
        return handled
    
    def update(self):
        if not self.isActive():
            return
        for graphObject in self._graphObjects:
            graphObject.update()        

class TextBox(GraphObject):
    def __init__(self, text, pos = Point((0, 0)), size = Size((100, 20)), font = Fonts.Arial12, bgColor = Colors.LightGray, fgColor = Colors.Black, orientation = Orientation.TopLeft):
        super().__init__(pos = pos, size = size, orientation = orientation)
        self._text = text
        self._font = font
        self._bgColor = bgColor
        self._fgColor = fgColor
        self._surface = PGSurface(self.size, alpha = 255)

    @property
    def backgroundColor(self):
        return self._bgColor

    @backgroundColor.setter
    def backgroundColor(self, value):
        self._bgColor = value


    @property
    def foregroundColor(self):
        return self._fgColor

    @foregroundColor.setter
    def foregroundColor(self, value):
        self._fgColor = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        
    def update(self):
        pass

    def drawBorder(self):
        self._surface.drawRect(Rect(Point((0, 0)), self.size), color=self.foregroundColor, width=2)
                               
    def draw(self, screen):
        self._surface.fill(self.backgroundColor)
        self.drawBorder()
        textSurface = self._surface.drawText(self._text, self.foregroundColor, self._font)
        textWidth = textSurface.get_width()
        textHeight = textSurface.get_height()
        textSize = Size((textWidth, textHeight))
        textPos = (self.size - textSize) / 2
        self._surface.paint(textSurface, tuple(textPos))
        super().paint(screen, self._surface._surface)
        
        
class Text(GraphObject):
    def __init__(self, text, pos = Point((0, 0)), font = Fonts.Arial14, color = Colors.White, orientation = Orientation.TopLeft):
        super().__init__(pos)
        self._text = text
        self._font = font
        self._color = color
        self._orientation = orientation

    def update(self):
        pass
    
    def draw(self, screen):
        surface = screen.drawText(self._text, self._color, self._font)
        super().paint(screen, surface)
        
class Sprite(GraphObject):
    def __init__(self, imagepath, pos = (0, 0), size = None):
        self._pos = pos
        self._size = size
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def set_left(self, value):
        self._pos[0] = value

    def set_top(self, value):
        self._pos[1] = value
        
    def set_pos(self, value):
        self._pos = value

    def left(self):
        return self._pos[0]
    
    def pos(self):
        return self._pos

    def top(self):
        return self._pos[1]

class PGRunner(GraphObject):
    def __init__(self, size : Size, backgroundColor = Colors.Black, backgroundImage = None):
        super().__init__(size = size, pos = Point((0,0)), parent = self)
        self._screen = PGScreen(self._size)
        self._running = False
        self._backgroundColor = backgroundColor
        self._backgroundImage = backgroundImage
        self._clock = pygame.time.Clock()
        self._eventHandler = []
        self.addEventHandler(self.eventHandler)
        self._graphObjects = []

    def addEventHandler(self, eventHandler):
        self._eventHandler.append(eventHandler)

    def addGraphObject(self, graphObject):
        self.debug(f"(graphObject={graphObject})")
        self._graphObjects.append(graphObject)

    @property
    def backgroundImage(self):
        return self._backgroundImage

    @backgroundImage.setter
    def backgroundImage(self, value):
        self._backgroundImage = value
        
    def setBackgroundColor(self, value):
        self.debug(f"(value={value}")
        self._backgroundColor = value

    def backgroundColor(self):
        return self._backgroundColor
    
    def set_running(self, value = True):
        self._running = value

    def running(self):
        return self._running

    def onKeyboardInterrupt(self):
        self.set_running(False)

    def onMouseDown(self, pos, button):
        self.debug(f"(pos={pos},button={button})")
        pass

    def onMouseMove(self, pos):
        pass

    def onQuit(self):
        self._running = False
        
    def handlePosEvent(self, event):
        for graphObject in self._graphObjects:
            if graphObject.rect().contains(Point(event.pos)):
                if graphObject.eventHandler(event):
                    return True
        return False
        
    def eventHandler(self, event):
        handled = self.handlePosEvent(event) if hasattr(event, "pos") else False
        if handled:
            return True

        handled = EventHandler.MapEvent(event, self)        
        
    def handleEvents(self):
        for event in pygame.event.get():
            for eventHandler in self._eventHandler:
                if eventHandler(event):
                    break
                
    def update(self):
        for graphObject in self._graphObjects:
            graphObject.update()

    def draw(self):
        self._screen.fill(self.backgroundColor())
        if self.backgroundImage != None:
            self._screen.drawImage(self.backgroundImage.image, (0, 0))
        for graphObject in self._graphObjects:
            graphObject.draw(self._screen)
            
    def run(self):
        self.set_running()
        self.debug("() enter")
        while self.running():
            try:
                self.handleEvents()
                self.update()
                self.draw()
                pygame.display.flip()
                self._clock.tick(60)
            except KeyboardInterrupt:
                self.set_running(False)
        self.debug("() leave")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = PGRunner(Size((800, 400)), Colors.LightBlue)
        runner.addGraphObject(Text("hello world", Point((400, 200)), font=Fonts.Arial64,orientation=Orientation.Center))
        runner.run()
    except Exception as e:
        logging.exception(f"caught exception: {e}")
    finally:
        pygame.quit()
        sys.exit()
