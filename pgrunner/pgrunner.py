import pygame
import sys
import os
import logging

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
    
class PGScreen:
    
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self.screen = pygame.display.set_mode((self._width, self._height))
        logging.debug(f"PGSCreen(screen={self.screen})")
        self._debugged = False

    def fill(self, color):
        if not self._debugged:
            logging.debug(f"PGSCreen.fill(screen={self.screen}, color={color})")
            self._debugged = True
        self.screen.fill(color)

    def drawText(self, text, pos, fgColor, font, orientation):
        surface = font.render(text, True, fgColor)
        return surface

    def paint(self, surface, pos):
        self.screen.blit(surface, pos)
        
class GraphObject:
    def __init__(self, pos = (0,0), size=None, orientation = Orientation.TopLeft):
        self._pos = pos
        self._size = size
        self._orientation = orientation

    def draw(self):
        pass

    def _getPosAtOrientation(self):
        if (self._orientation & Orientation.HCenter) == Orientation.HCenter:
            x = self._pos[0] - self._size[0] / 2
        elif (self._orientation & Orientation.Left) == Orientation.Left:
            x = self._pos[0]
        elif (self._orientation & Orientation.Right) == Orientation.Right:
            x = self._pos[0] - self._size[0]
        else:
            x = self._pos[0]
        if (self._orientation & Orientation.VCenter) == Orientation.VCenter:
            y = self._pos[1] - self._size[1]/2
        elif (self._orientation & Orientation.Top) == Orientation.Top:
            y = self._pos[1]
        elif (self._orientation & Orientation.Bottom) == Orientation.Bottom:
            y = self._pos[1] - self._size[1]
        else:
            y = self._pos[1]

        return x, y
        
    def paint(self, screen, surface):
        width = surface.get_width()
        height = surface.get_height()
        self._size = (width, height)
        x, y = self._getPosAtOrientation()
        screen.paint(surface, [x, y])
        
    def setPos(self, pos):
        self._pos = pos

    def pos(self):
        return self._pos

    def setSize(self, size):
        self._size = size
        
    def size(self):
        return self._size

class Text(GraphObject):
    def __init__(self, text, pos = (0, 0), font = Fonts.Arial14, color = Colors.White, orientation = Orientation.TopLeft):
        super().__init__(pos)
        self._text = text
        self._font = font
        self._color = color
        self._orientation = orientation

    def update(self):
        pass
    
    def draw(self, screen):
        surface = screen.drawText(self._text, self._pos, self._color, self._font, self._orientation)
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
    def __init__(self, width, height, backgroundColor = Colors.Black):
        self._width = width
        self._height = height
        self._screen = PGScreen(width, height)
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
    
    def eventHandler(self, event):
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
        runner = PGRunner(800, 400, Colors.LightBlue)
        runner.addGraphObject(Text("hello world", (400, 200), font=Fonts.Arial64,orientation=Orientation.Center))
        runner.run()
    except Exception as e:
        print(e)
    finally:
        pygame.quit()
        sys.exit()
