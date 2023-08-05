import pgzrun
from enum import Enum
import logging

WIDTH = 1024
HEIGHT = 768

screenAspect = float(WIDTH) / float(HEIGHT)
xWidth = 10.0
yWidth = xWidth / screenAspect
xAspect = 10.0 / float(WIDTH)
yAspect = yWidth / float(HEIGHT)
wallWidth = 0.22

class Direction(Enum):
    Horizontal = 1
    Vertical = 2
    
class Position:

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def __repr__(self):
        return f"<Position x:{self._x} y:{self._y})>"

    def __str__(self):
        return f"Position(x={self._x}, y={self._y})"

class Size:
    def __init__(self, dx, dy):
        self._dx = dx
        self._dy = dy

    def set_dx(self, dx):
        self._dx =dx

    def set_dy(self, dy):
        self._dy = dy

    def dx(self):
        return self._dx

    def dy(self):
        return self._dy

    def __repr__(self):
        return f"<Size dx:{self._dx}, dy={self._dy}>"
    
    def __str__(self):
        return f"Size(dx={self._dx}, dy={self._dy})"
                
    
def draw():
    screen.clear()
    screen.fill((255,255,255))
    drawRoom(Position(1.0, 1.0), Size(4.67, 4.00))
        
def drawRoom(pos, size):
    logging.debug(f"drawRoom(pos={pos},size={size}), wallWidth={wallWidth}")
    pos1 = drawWall(pos, size.dx(), Direction.Horizontal)
    pos2 = drawWall(pos, size.dy(), Direction.Vertical)
    drawWall(Position(pos1.x(), pos.y()), size.dy(), Direction.Vertical)
    drawWall(Position(pos.x(), pos2.y()), size.dx(), Direction.Horizontal)

def getScreenPos(pos):
    logging.debug(f"getScreenPos(pos={pos}), xAspect={xAspect}, yAspect={yAspect}")
    result = (int(pos.x() / xAspect), int(pos.y() / yAspect))
    return result

def drawWall(pos, length, direction):
    logging.debug("drawWall(pos=%s, length=%d, direction=%s)" % (pos, length, direction))
    x0 = float(pos.x()) - float(wallWidth)
    logging.debug(f"x0=float({pos.x()} - float({wallWidth}) = {x0}")
    y0 = float(pos.y()) - float(wallWidth)
    if direction == Direction.Horizontal:
        width = length + 2 * wallWidth
        height = wallWidth
    else:
        width = wallWidth
        height = length + 2*wallWidth
    logging.debug("edges of real wall: (%d|%d,%d|%d)" % (x0, y0, width, height))
    pos0 = getScreenPos(Position(x0, y0))
    screenSize = getScreenPos(Position(width, height))
    logging.debug("edges on screen: (%d|%d,%d|%d)" % (pos0[0],pos0[1], screenSize[0], screenSize[1]))
    screen.draw.rect(Rect(pos0[0], pos0[1], screenSize[0], screenSize[1]), (0,0,0))
    return Position(x0 + width, y0 +  height)
    

logging.basicConfig(level=logging.DEBUG)
pgzrun.go()
