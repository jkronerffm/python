from imports import *

class SenderList(GraphObjectGroup):
    def onMouseDown(self, pos, button):
        self.debug(f"(pos={pos})")

class Controls(GraphObjectGroup):
    def __init__(self, pos : Point, size : Size, orientation : Orientation, backgroundColor, alpha):
        super().__init__(pos=pos, size=size, orientation=orientation, backgroundColor=backgroundColor, alpha=alpha)
        self.addGraphObject(TextBox("Hello World", pos=Point(tuple(size)), size=Size((100, 20)), font=Fonts.Arial14,orientation=Orientation.BottomRight, bgColor = Colors.LightGray, fgColor=Colors.Black))
        
    def onMouseDown(self, pos, button):
        self.debug(f"(pos={pos})")
        return True

class Radio(GraphObjectGroup):
    def __init__(self,
               size = None,
               pos = Point((0,0)),
               orientation = Orientation.TopLeft,
               active=True):
        self.debug(f"(size={size},pos={pos},orientation={orientation})")
        super().__init__(size=size,
                         pos=pos,
                         orientation=orientation,
                         backgroundColor=Colors.Black,
                         alpha=0,
                         active=active)
        self.addGraphObject(SenderList(size = Size((size.width, size.height/2)), pos = Point(tuple(size/2)), orientation = Orientation.BottomCenter, backgroundColor = Colors.Black, alpha=0))
        self.addGraphObject(Controls(size = Size((size.width, size.height/2)), pos = Point(tuple(size/2)), orientation = Orientation.TopCenter, backgroundColor = Colors.Black, alpha=0))

    def onMouseDown(self, pos, button):
        self.debug(f"(pos={pos}, button={button})")
        return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = PGRunner(Size((1024,768)),
                          Colors.Black,
                          PGImage(Size((1024,768)),"/var/radio/background/radiobg1.jpg"))
        runner.addGraphObject(Radio(pos = Point(tuple(runner.size/2)),
                                    size = Size((1024, 768)),
                                    orientation = Orientation.Center))
        
        runner.run()
    except Exception as e:
        logging.exception(f"caught exception: {e}")
    finally:
        pygame.quit()
        sys.exit()

