import subprocess
import logging
import os

class XSet:
    def __init__(self):
        self._display = os.environ['DISPLAY']
        pass

    def toggle(self, on = True):
        onoff = "on" if on else "off"
        output = subprocess.run(["xset",
                                 "-display",
                                 self._display,
                                 "dpms",
                                 "force",
                                 onoff], capture_output = True)
        return output

    def display(self):
        return self._display
    
    def on(self):
        return self.toggle(True)

    def off(self):
        return self.toggle(False)

if __name__ == "__main__":
    import time
    xset = XSet()
    for task in [lambda s: s.display(),
                 lambda s: s.off(),
                 lambda s: s.on()]:
        print(task(xset))
        time.sleep(3)
    
