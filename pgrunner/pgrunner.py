import pygame
import sys
import os
import logging
from graphs import *

pygame.init()

class Colors:
    Black = (0, 0, 0)
    White = (255, 255, 255)
    Blue = (0, 0, 255)
    LightBlue = (173, 216, 230)

class Fonts:
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
    
class PGSurface:
    
    def __init__(self, size : Size):
        self._size = size
        self._surface = self.getSurface()
        logging.debug(f"PGSCreen(screen={self._surface}, size={self.size()})")

    def getSurface(self):
        return pygame.Surface(self.size())
    
    def fill(self, color):
        self._surface.fill(color)

    def drawText(self, text, fgColor, font):
        surface = font.render(text, True, fgColor)
        return surface

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

class GraphObject:
    def __init__(self, pos : Point((0, 0)), size : Size = None, orientation = Orientation.TopLeft, active = True):
        self._pos = pos
        self._size = size
        self._orientation = orientation
        self._active = active
        logging.debug(f"GraphObject.__init__(pos={self._pos}, size={self._size})")

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
        result = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = self.onMouseDown(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            result = self.onMouseUp(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            result = self.onMouseMove(event.pos)

        return result
        
    def _getPosAtOrientation(self):
        if (self._orientation & Orientation.HCenter) == Orientation.HCenter:
            x = self._pos.x() - self._size.width() / 2
        elif (self._orientation & Orientation.Left) == Orientation.Left:
            x = self._pos.x()
        elif (self._orientation & Orientation.Right) == Orientation.Right:
            x = self._pos.x() - self._size.width()
        else:
            x = self._pos.x()
        if (self._orientation & Orientation.VCenter) == Orientation.VCenter:
            y = self._pos.y() - self.height()/2
        elif (self._orientation & Orientation.Top) == Orientation.Top:
            y = self._pos.y()
        elif (self._orientation & Orientation.Bottom) == Orientation.Bottom:
            y = self._pos.y() - self._size.height()
        else:
            y = self._pos.y()

        return x, y
        
    def paint(self, screen, surface):
        width = surface.get_width()
        height = surface.get_height()
        self._size = Size((width, height))
        x, y = self._getPosAtOrientation()
        screen.paint(surface, [x, y])
        
    def setPos(self, pos):
        self._pos = pos

    def left(self):
        return self._pos.x()

    def top(self):
        return self._pos.y()

    def right(self):
        return self.left() + self.width()

    def bottom(self):
        return self.top() + self.height()
    
    def pos(self):
        return self._pos

    def setSize(self, size : Size):
        self._size = size
        
    def size(self):
        return self._size

    def width(self):
        return self._size.width()

    def height(self):
        return self._size.height()

    def rect(self):
        x,y = self._getPosAtOrientation()
        return Rect(Point((x,y)), self._size)

class GraphObjectGroup(GraphObject):
    def __init__(self, size : Size, pos = Point((0,0)), orientation = Orientation.TopLeft, backgroundColor = Colors.Black, active=True):
        super().__init__(pos, size, orientation, active=active)
        self._backgroundColor = backgroundColor
        self._graphObjects = []
        self._surface = PGSurface(self.size())
        logging.debug(f"GraphObjectGroup.__init__(pos={self._pos}, size={self._size})")
        
    def addGraphObject(self, graphObject):
        self._graphObjects.append(graphObject)

    def draw(self, screen):
        if not self.isActive():
            return
        
        self._surface.fill(self._backgroundColor)
        for graphObject in self._graphObjects:
            graphObject.draw(self._surface)
        super().paint(screen, self._surface.surface())

    def eventHandler(self, event):
        handled = False
        for graphObject in self._graphObjects:
            if graphObject.rect().contains(Point(event.pos)):
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
        
class Sprite:
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

class PGRunner:
    def __init__(self, size : Size, backgroundColor = Colors.Black):
        self._size = size
        self._screen = PGScreen(self._size)
        self._running = False
        self._backgroundColor = backgroundColor
        self._clock = pygame.time.Clock()
        self._eventHandler = []
        self.addEventHandler(self.eventHandler)
        self._graphObjects = []

    def addEventHandler(self, eventHandler):
        self._eventHandler.append(eventHandler)

    def addGraphObject(self, graphObject):
        logging.debug(f"PGRunner.addGraphObject(graphObject={graphObject})")
        self._graphObjects.append(graphObject)
        
    def setBackgroundColor(self, value):
        logging.debug(f"setBackgroundColor(value={value}")
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
        logging.debug(f"onMouseDown(pos={pos},button={button})")
        pass

    def onMouseMove(self, pos):
        pass

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
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.onMouseDown(event.pos, event.button)
            return True
        elif event.type == pygame.MOUSEMOTION:
            self.onMouseMove(event.pos)
            return True
        else:
            return False
        
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
        for graphObject in self._graphObjects:
            graphObject.draw(self._screen)
            
    def run(self):
        self.set_running()
        logging.debug("PGRunner.run() enter")
        while self.running():
            try:
                self.handleEvents()
                self.update()
                self.draw()
                pygame.display.flip()
                self._clock.tick(60)
            except KeyboardInterrupt:
                self.set_running(False)
        logging.debug("PGRunner.run() leave")

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
