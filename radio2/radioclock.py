from imports import *
from Clock import Clock

class RadioClock(PGRunner):

    def __init__(self):
        super().__init__(Size((800, 400)), Colors.Black)
        self.addGraphObject(Clock(size=Size((800, 400)), pos = Point((0, 0))))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        runner = RadioClock()
        runner.run()
    except Exception as e:
        logging.exception(e)
    finally:
        pygame.quit()
        sys.exit()
