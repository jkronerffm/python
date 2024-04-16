import subprocess
import logging
import os
import inspect
import time
import shlex

class XSet:
    def __init__(self, delay = 0.1):
        self._display = os.environ['DISPLAY']
        self._delay = delay
        pass

    def toggle(self,on):
        result  = self.off() if not on else self.on()
        return result
    
    def display(self):
        return self._display

    def _executeOnOff(self, onOff):
        command = f"xset -display {self._display} dpms force {onOff}"
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}(command={command})")
        output = subprocess.run(command.split(), capture_output = True)
        return output.returncode

    def _executePiped(self, commands):
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}()")
        inputStream = None
        cmd = None
        for command in commands:
            logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}(command={command})")
            cmd = subprocess.Popen(shlex.split(command), stdin = inputStream, stdout = subprocess.PIPE, text=True)
            inputStream = cmd.stdout
        out, err = cmd.communicate()
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}() --> {out}")        
        return out.strip()
    
    def off(self):
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}()")
        return self._executeOnOff("off")

    def on(self):
        logging.debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}()")
        return self._executeOnOff("on")

    def getMonitorState(self):
        commands = [
                    "xset -q",
                    "grep -C3 -i 'DPMS'",
                    "grep Monitor",
                    "sed 's/^ *//'",
                    "cut -d' ' -f3"
                ]
        return self._executePiped(commands)
    
if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    xset = XSet()
    for task in [{'delay': 0,
                  'cmd': lambda s: s.getMonitorState()
                 }, {'delay': 5,
                  'cmd': lambda s: s.display()
                 }
##                 ,{'delay': 30,
##                  'cmd': lambda s: s.off()
##                 },
##                 {'delay': 0,
##                  'cmd': lambda s: s.on()
##                 }
                 ]:
        print(task['cmd'](xset))
        time.sleep(task['delay'])
    
