import os
import psutil
import signal
import logging

class Daemon:
    def __init__(self, name, command=None):
        logging.debug(f"{self.__class__.__name__}.__init__(name={name})")
        self._name = name
        self._command = command if command != None else f"{name}d"
        self._pid = None
        self._started = False

    def __str__(self):
        return f"Daemon(name={self.name()}, pid={self.getPid()})"

    def clear(self):
        self._name = None
        self._command = None
        self._pid = None
        self._started = False
        
    def name(self):
        return self._name

    def command(self):
        return self._command
    
    def start(self):
        logging.debug(f"{self.__class__.__name__}.start()")
        pid = self.getPid()
        if pid == None:
            os.system(f"sudo {self._command}")
            pid = self.getPid()
            self._started = True
        return pid

    def hasStarted(self):
        return self._started
    
    def kill(self):
        if self.hasStarted():
            logging.debug(f"kill daemon with pid {self.getPid()}")
            os.system(f"sudo kill -9 {self.getPid()}")
            self.clear()        
        
    def getPid(self):
        if self._pid == None:
            pid = [p.pid for p in psutil.process_iter(['pid', 'name']) if p.name().startswith(self._name)]
            
            self._pid = pid[0] if len(pid) == 1 else None

        return self._pid

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    d = Daemon("pigpio")
    pid = d.start()
    if d.hasStarted():
        logging.debug(f"{str(d)} started successfully")
    else:
        logging.debug(f"{str(d)} was already running")
    
    d.kill()
