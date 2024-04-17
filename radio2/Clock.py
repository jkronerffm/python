from imports import *
from time import localtime, strftime

class Time(Text):
    def __init__(self):
        super().__init__("", pos=Point((400, 200)),font = Fonts.Arial128, orientation = Orientation.BottomCenter)

    def update(self):
        now = localtime()
        time = strftime("%H:%M", now)
        self._text = time

    def draw(self, surface):
        super().draw(surface)

    def onMouseDown(self, pos, button):
        logging.debug(f"{self.__class__.__name__}.onMouseDown(pos={pos}, button={button})")
        return True

class Date(Text):
    def __init__(self):
        super().__init__("", pos=Point((400, 200)), font = Fonts.Arial64, orientation = Orientation.TopCenter)

    def update(self):
        now = localtime()
        date = strftime("%d.%m.%Y", now)
        self._text = date

    def draw(self, surface):
        super().draw(surface)

    def onMouseDown(self, pos, button):
        self.debug(f"(pos={pos}, button={button})")
        return True
    
class Clock(GraphObjectGroup):
    def __init__(self, size = None, pos = Point((0, 0)), orientation = Orientation.TopLeft, active=True):
        logging.debug(f"Clock.__init__(size={size}, pos={pos})")
        super().__init__(pos=pos, size=size, orientation=orientation, backgroundColor = Colors.Black, active = active)
        self.addGraphObject(Date())
        self.addGraphObject(Time())

    def onMouseDown(self, pos, button):
        logging.debug(f"{self.__class__.__name__}.onMouseDown(pos={pos}, button={button})")
        return True
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = PGRunner(Size((1024, 768)), Colors.Black)
        runner.addGraphObject(Clock(size = Size((800, 400)), pos=Point(tuple(runner.size()/2)), orientation = Orientation.Center))
        runner.run()
    except Exception as e:
        logging.exception(f"caught exception: {e}")
    finally:
        pygame.quit()
        sys.exit()
    
