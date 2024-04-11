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

    def __str__(self):
        return f"Point(x={self._x}, y={self._y})"

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Point(x=self.x() + other.x(), y=self.y() + other.y())
        else:
            raise TypeError("Unsupported operand type(s) for +")
    
class Size:
    def __init__(self, size = None, width = 0, height=0):
        if size != None:
            self._width = size[0]
            self._height = size[1]
        else:
            self._width = width
            self._height = height
            
    def __str__(self):
        return f"Size(width={self._width}, height={self._height})"
    
    def width(self):
        return self._width

    def height(self):
        return self._height

    def setWidth(self, value):
        self._width = value

    def setHeight(self, value):
        self._height = value

    def __iter__(self):
        yield self._width
        yield self._height
    
class Rect:
    def __init__(self, point : Point, size : Size):
        self._point = point
        self._size = size

    def x(self):
        return self._point.x()

    def left(self):
        return self.x()

    def right(self):
        return self.x() + self.width()

    def top(self):
        return self.y()

    def bottom(self):
        return self.y() + self.height()
    
    def setX(self, value):
        self._point.setX(value)
        
    def y(self):
        return self._point.y()

    def setY(self, value):
        self._point.setY(value)

    def width(self):
        return self._size.width()

    def setWidth(self, value):
        self._size.setWidth(value)

    def height(self):
        return self._size.height()

    def setHeight(self, value):
        self._size.setHeight(value)

    def point(self):
        return self._point

    def setPoint(self, value):
        self._point = value
        
    def size(self):
        return self._size
    
    def setSize(self, value):
        self._size = value

    def __iter__(self):
        yield self._point.x()
        yield self._point.y()
        yield self._size.width()
        yield self._size.height()
        
    def __str__(self):
        return f"Rect(point={str(self._point)}, size={str(self._size)})"

    def contains(self, point : Point):
        return (point.x() >= self.left() and point.y() >= self.top()) and (point.x() <= self.right() and point.y() <= self.bottom())
    
if __name__ == "__main__":
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
