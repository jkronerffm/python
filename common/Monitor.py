import multiprocessing
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from socket import *
from threading import Thread, Lock
from xrandr import XRandr
from XSet import XSet
import logging
from logging import handlers
import inspect
import dictToObj
from LogFormatter import LogFormatter
import secrets
import sys
import os
import time
import getopt
import datetime
from AnsiColors import Color, BGColor, Colors

class Monitor:
    """
    The class Screen supports some functions on Screen.

    Attributes
    ----------
    _xrandr : XRandr
        calls some functions on command xrandr
    _xset : XSet
        calls some functions on command xset
    _name : str
        the name of connected display returned from xrandr
    _dimValue : float
        the brightness value of dimmed screen.
    _currentValue : float
        the current value of brightness
    _lightValue : float
        the brightness value of lighted screen.
    _on : the current on-/off-state of screen
    
    """
    
    def __init__(self, delay=0.1):
        """
        Initializes the Screen object. To perform functions on Screen it
        generates objects of type XRandr and XSet. To perform operations
        on XRandr it gets the name as output from XRandr. To perform on
        XSet it gets the display from environment variable $DISPLAY

        Initializes the object variables.
        """
        
        logging.debug(f"{self.__class__.__name__}.__init__()")
        self._xrandr = XRandr()
        self._xset = XSet(delay=delay)
        self._name = self._xrandr.getOutput()
        self._dimValue = 0.2
        self._lightValue = 1.0
        self._on = self.getState()
        self._currentValue = self._xrandr.getBrightness(self._name)

    def name(self):
        """
        Returns the name of xrandr output
        """
        
        return self._name
    
    def dimValue(self):
        """
        Returns the value of dimmed brightness
        """
        
        return self._dimValue
        
    def lightValue(self):
        """Returns the value of lighted brightness"""
        
        return self._lightValue
        
    def setCurrentValue(self, value):
        """Sets current value of brightness. Sets the brightness of screen via xrandr."""
        
        self._currentValue = value
        self._xrandr.setBrightness(self._name, self._currentValue)
        
    def setDimValue(self, value):
        """
        Sets the value of dimmed brightness.

        If currenly screen is dimmed the new value will be activated immediately.
        """
        
        if self._currentValue == self._dimValue:
            self.setCurrentValue(value)
        self._dimValue = value
        
    def setLightValue(self, value):
        """
        Sets the value of lighted brightness.

        If currenly screen is lighted the new value will be activated immediately.
        """
        
        if self._currentValue == self._lightValue:
            self.setCurrentValue(value)
        self._lightValue = value
        
    def toggleBrightness(self):
        """
        Toggles the brightness.
        """
        
        newValue = self._dimValue if self._currentValue == self._lightValue else self._lightValue
        logging.debug(f"Brightness.toggle(currentValue={self._currentValue}, newValue={newValue})")
        self.setCurrentValue(newValue)

    def isOn(self):
        """
        Returns if screen is currently switched on.
        """
        
        return self._on
    
    def toggle(self):
        """
        Toggles the screen between on and off
        """

        toggleTo = not self.isOn()
        logging.debug(f"{self.__class__.__name__}.toggle(toggleTo={toggleTo})")
        self._xset.toggle(toggleTo)
        self._on = toggleTo
        logging.debug(f"{self.__class__.__name__}.toggle(on={self.isOn()})")
        return self.isOn()

    def on(self):
        """
        Turns on the screen
        """

        logging.debug(f"{self.__class__.__name__}.on()")
        self._xset.on()
        self._on = True
        return True

    def off(self):
        """
        Turns off the screen.
        """

        logging.debug(f"{self.__class__.__name__}.off()")
        self._xset.off()
        self._on = False
        return False
        
    def dim(self):
        """
        Dims the screen.
        """
        self.setCurrentValue(self._dimValue)

    def light(self):
        """
        Lightens the screen.
        """
        
        self.setCurrentValue(self._lightValue)

    def getState(self):
        return self._xset.getMonitorState().casefold() == "on".casefold()

class ClientServer:
    Port = 6100
    Timeout = 3
    VarPath = "/var/radio"
    ConfDir = "conf"
    Filename = "monitor.json"
    
    def __init__(self, fgColor, bgColor):
        clr = Colors()
        self._color = clr(fgColor, bgColor)

    def debug(self, msg):
        logging.debug(self._color + f"{self.__class__.__name__}.{inspect.stack()[1][3]}{msg}" + Colors.Reset)

    def GetConfPath():
        confFilepath = os.path.join(ClientServer.VarPath, ClientServer.ConfDir, ClientServer.Filename)
        return confFilepath

    def GetConfig():
        return dictToObj.objFromJson(ClientServer.GetConfPath())
    
class Server(ClientServer):
    def __init__(self, timeout=ClientServer.Timeout):
        super().__init__(Color.Black, BGColor.Green)
        super().debug("()")
        monitorConf = self.__class__.GetConfig()
        self._port = monitorConf.port
        address = ('localhost', self._port)
        self._listener = Listener(address, authkey=bytes(monitorConf.authkey, "utf-8"))
        self._listener._listener._socket.settimeout(timeout)
        self._running = False

    def isRunning(self):
        return self._running

    def onMessageOn(self):
        super().debug(f"()")
        return self._monitor.on()

    def onMessageOff(self):
        super().debug(f"()")
        return self._monitor.off()

    def onMessageStatus(self):
        super().debug(f"()")
        state = self._monitor.getState()
        return state

    def performMessages(self, connection):
        connected = True
        while connected:
            msg = connection.recv()
            super().debug(f"(msg={msg})")
            if msg == "0" or len(msg) == 0:
                super().debug(f"(): connection has been closed by client")
                connected = False
                continue
            result = self.handleMessage(msg)
            if result != None:
                connection.send(str(result))
        
    def handleClient(self):
        ##super().debug(f"{self.__class__.__name__}.{inspect.stack()[0][3]}()")
        try:
            with self._listener.accept() as connection:
                super().debug(f"(): client is connected")
                self.performMessages(connection)
        except EOFError:
               super().debug(f"(): connection closed by client!")
        except error:
            pass
            ##super().debug(f"(): no connection. Continue...")
        except Exception as e:
            super().debug(f"(e=(typename={type(e).__name__},classname={e.__class__.__name__}, qualname={e.__class__.__qualname__})): error occured")
            
    def handleMessage(self, msg):
        super().debug(f"(msg={msg})")
        if msg == "on":
            return self.onMessageOn()
        elif msg == "off":
            return self.onMessageOff()
        elif msg == "state":
            return self.onMessageStatus()
        
    def run(self):
        super().debug(f"()")
        self._monitor = Monitor()
        self._running = True
        while self.isRunning():
            time.sleep(1)
            self.handleClient()

    def stop(self):
        self._running=False
        
class Client(ClientServer):
    _Instance = None
    
    def __init__(self):
        super().__init__(Color.Black, BGColor.Red)
        super().debug(f"()")
        monitorConf = self.__class__.GetConfig()
        self._offTime = monitorConf.time.off if monitorConf.time.off != "test" else datetime.datetime.now().strftime("%H:%M")
        self._onTime = monitorConf.time.on if monitorConf.time.on != "test" else (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%H:%M")
        self._onTime2 = monitorConf.time.on2
        self._delayOffTime = int(monitorConf.time.delayOff) if hasattr(monitorConf.time, "delayOff") else 10
        self._port = monitorConf.port
        address = ('localhost', self._port)
        self._client = multiprocessing.connection.Client(address, authkey = bytes(monitorConf.authkey,'utf-8'))
        super().debug(f"(client={self._client})")

    def __del__(self):
        super().debug(f"()")

    @classmethod
    def GetInstance(cls):
        if cls._Instance == None:
            cls._Instance = Client()

        return cls._Instance
    
    def queryService(self, service, requireResponse = True):
        super().debug(f"(service={service})")
        self._client.send(service)
        response = self._client.recv() if requireResponse else None
        super().debug(f"(response={response})")
        return response != None and response.lower() in ['true', 'on', '1', 'yes', 'ok']
    
    def on(self):
        super().debug(f"()")
        return self.queryService("on")

    def off(self):
        super().debug(f"()")
        return self.queryService("off")

    def status(self):
        super().debug(f"()")
        return self.queryService("state")
    
    def isOn(self):
        super().debug(f"()")
        status = self.status()
        value = status
        super().debug(f"(status={status}) --> {value}")
        return value

    def toggle(self):
        super().debug(f"()")
        result = None
        if self.isOn():
            result = self.off()
        else:
            result = self.on()
        super().debug(f"() --> {result}")
        return result

    def switch(self, on):
        super().debug(f"(on={on})")
        if not on and self.isOn():
            return self.off()
        elif on and not self.isOn():
            return self.on()

    def getDelayOffTime(self):
        return self._delayOffTime
    
    def getOffTime(self):
        return self._offTime

    def getOnTime(self):
        return self._onTime

    def getOnTime2(self):
        return self._onTime2

    def isOffTime(self):
        now = datetime.datetime.now().strftime("%H:%M")
        result = now >= self.getOffTime() and now < self.getOnTime()
        super().debug(f"(now={now},offTime={self.getOffTime()}, onTime={self.getOnTime()}) --> {result}")
        return result
        
def createAuthKey(renew = False):
    monitorConf = dictToObj.objFromJson(ClientServer.GetConfPath())
    logging.debug(f"(monitorConf={monitorConf})")
    if not hasattr(monitorConf, "authkey") or renew:
        authKey = secrets.token_urlsafe(16)
        monitorConf.authkey = authKey

    if not hasattr(monitorConf, "port"):
        monitorConf.port = Server.Port
        
    dictToObj.objToJsonFile(monitorConf, Server.GetConfPath())


if __name__ == "__main__":
    import time

    print("start Monitor.Server...")
    opts, args = getopt.getopt(sys.argv[1:], "dt:", ["debug", "timeout="])
    debugging = False
    timeout = ClientServer.Timeout
    for opt,arg in opts:
        print(opt, arg)
        if opt in ('-d', '--debug'):
            debugging = True
        elif opt in ('-t', '--timeout'):
            timeout = int(arg)

    level = logging.DEBUG if debugging else logging.FATAL
    logger = logging.getLogger()
    logger.setLevel(level)
    logFormatter = LogFormatter()    
    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    console_handler.setFormatter(logFormatter)
    logging.basicConfig(level=level)
    createAuthKey()

    logging.debug("start server...")
    server = Server(timeout)
    try:
        server.run()
    except KeyboardInterrupt:
        logging.debug("Stop the server...")
        server.stop()
