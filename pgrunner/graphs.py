import logging
import inspect

class Point:
    def __init__(self, pos = None, x = 0, y = 0):
        if pos != None:
            self._x = pos[0]
            self._y = pos[1]
        else:
            self._x = x
            self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def set(self, value : tuple):
        self._x = value[0]
        self._y = value[1]
        
    def setX(self, value):
        self._x = value

    def setY(self, value):
        self._y = value

    def __iter__(self):
        yield self._x
        yield self._y

    def __repr__(self):
        return f"Point(x={self._x}, y={self._y})"

    def __str__(self):
        return f"({self._x}, {self._y})"
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Point(x=self.x() + other.x(), y=self.y() + other.y())
        else:
            raise TypeError("Unsupported operand type(s) for +")

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Point(x = self.x() - other.x(), y = self.y() - other.y())
        else:
            raise TypeError("Unsupported operand type(s) for -")

class Size:
    def __init__(self, size = None, width = 0, height=0):
        if size != None:
            self._width = size[0]
            self._height = size[1]
        else:
            self._width = width
            self._height = height
            
    def __repr__(self):
        return f"Size(width={self._width}, height={self._height})"

    def __str__(self):
        return f"({self._width}, {self._height})"
    
    def width(self):
        return self._width

    def height(self):
        return self._height

    def setWidth(self, value):
        self._width = value

    def setHeight(self, value):
        self._height = value

    def __truediv__(self, value):
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}(type(value) = {type(value)})")
        if isinstance(value, int):
            return Size((int(self.width() / value), int(self.height() / value)))
        else:
            raise TypeError("Unsupported operand type(s) for /")

    def __iter__(self):
        yield self._width
        yield self._height
    
class Rect:
    def __init__(self, pos : Point, size : Size):
        self._pos = pos
        self._size = size

    def x(self):
        return self._pos.x()

    def left(self):
        return self.x()

    def right(self):
        return self.x() + self.width()

    def top(self):
        return self.y()

    def bottom(self):
        return self.y() + self.height()
    
    def setX(self, value):
        self._post.setX(value)
        
    def y(self):
        return self._pos.y()

    def setY(self, value):
        self._pos.setY(value)

    def width(self):
        return self._size.width()

    def setWidth(self, value):
        self._size.setWidth(value)

    def height(self):
        return self._size.height()

    def setHeight(self, value):
        self._size.setHeight(value)

    def pos(self):
        return self._pos

    def setPos(self, value):
        self._pos = value
        
    def size(self):
        return self._size
    
    def setSize(self, value):
        self._size = value

    def __iter__(self):
        yield self._pos.x()
        yield self._pos.y()
        yield self._size.width()
        yield self._size.height()
        
    def __repr__(self):
        return f"Rect(pos={repr(self._pos)}, size={repr(self._size)})"

    def __str__(self):
        return f"({str(self._pos)}, {str(self._size)})"
    
    def contains(self, point : Point):
        return (point.x() >= self.left() and point.y() >= self.top()) and (point.x() <= self.right() and point.y() <= self.bottom())

    def surfaceToRect(self, point : Point):
        return point - self.pos()

    def rectToSurface(self, point : Point):
        return self.pos() + point
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    p1 = Point(x=10, y=20)
    print(p1)
    print(p1.x(), p1.y())
    p1.setX(30)
    print(p1)
    p2 = Point((50, 40))
    print(p2)
    p3 = p1 + p2
    print(f"{p1} + {p2} = {tuple(p3)}")
    s1 = Size((40, 40))
    print(f"{s1} = {tuple(s1)}")
    r1 = Rect(p1, s1)
    print(f"{r1} = {tuple(r1)}")
    print(f"rect: {r1.left()}, {r1.top()}, {r1.right()}, {r1.bottom()}")
    for point in [p1, p2, p3]:
        print(f"point={tuple(point)} is in r1{tuple(r1)} => {r1.contains(point)}")

    r = Rect(Point((50,50)), Size((800, 400)))
    p1 = Point((100, 100))
    p2 = r.surfaceToRect(p1)
    print(f"r={r}, p={p1}, pointToRect->{p2}")
    r.setPos(Point((100, 100)))
    p2 = r.surfaceToRect(p1)
    print(f"r={r}, p={p1}, pointInRect->{p2}")
    p3 = r.rectToSurface(p2)
    print(f"rectToSurface --> {p3}")
    s = Size((1024, 768))
    logging.debug("try division")
    try:
        sd = s / 2
        pd = Point(tuple(sd))
        print(f"{repr(s)} / 2 = {repr(sd)} = {repr(pd)}")
    except Exception as e:
        logging.exception(e)
