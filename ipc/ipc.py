import multiprocessing
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from threading import Thread, Lock
import time
import getopt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "common"))
import dictToObj
import logging
##import secrets
##import string

class StatusServer:
    AuthKey = b'WmQokj4EzJ8RnD2OQSuJ'
    Port = 6001
    Host = 'localhost'
    
    def __init__(self, name, statusCallback):
        address = (StatusServer.Host, StatusServer.Port)
        self._listener = Listener(address, authkey=StatusServer.AuthKey)
        self._name = name
        self._running = False
        self.lock = Lock()
        self._statusCallback = statusCallback
        
    def __str__(self):
        return f"<{__class__.__name__}(name={self._name})"
    
    @staticmethod
    def Run(server):
        logging.debug(f"StatusServer.Run(server={server})")
        server.run()
        
    def run(self):
        logging.debug(f"{self.__class__.__name__}.run()")
        self.setRunning(True)
        while self.running():
            time.sleep(1)
            with self._listener.accept() as conn:
                logging.debug(f"{self.__class__.__name__}.run(): connection accepted from {self._listener.last_accepted}")
                while True:
                    msg = conn.recv()
                    logging.debug(f"{self.__class__.__name__}.run(msg={msg})")
                    if msg == 'status':
                        data = self._statusCallback() if not (self._statusCallback == None) else "unavailable"
                        conn.send(data)
                    elif msg == 'close':
                        conn.close()
                        break
                    elif msg == 'exit':
                        conn.close()
                        self._listener.close()
                        self.setRunning(False)
                        break

    def running(self):
        value = False
        self.lock.acquire()
        value = self._running
        self.lock.release()
        return value

    def setRunning(self, value):
        self.lock.acquire()
        self._running = value
        self.lock.release()
        
    @staticmethod
    def StartThread(name, statusCallback):
        logging.debug("Server.StartThread()")
        server = StatusServer(name, statusCallback)
        server.setRunning(True)
        t = Thread(target = StatusServer.Run, args=[server], daemon=True)
        t.start()
        return server

class StatusClient:

    def __init__(self, statusCallback):
        logging.debug(f"{self.__class__.__name__}()")
        address = (StatusServer.Host, StatusServer.Port)
        self._client = multiprocessing.connection.Client(address, authkey=StatusServer.AuthKey)
        self._statusCallback = statusCallback

    def run(self, doExit=False):
        logging.debug("Client.run()")
        self._client.send('status')
        msg = self._client.recv();
        if self._statusCallback is not None:
            self._statusCallback(msg)
        self._client.send('exit' if doExit else 'close')

def serverStatusCallback():
    return {"running": True, "currentsender": "hr1", "volume": 75, "equalizer": "Full bass", "nextwaketime": "22.02.2024 05:30"}

def clientStatusCallback(statusData):
    print(f"clientStatusCallback(statusData=<{type(statusData)}({str(statusData)})>)")
    
def runServer():
    logging.debug("runServer")
    server = StatusServer.StartThread("test", serverStatusCallback)
    print("press Ctrl-C to interrupt")
    while server.running():
        try:
            print(".", end="")
            time.sleep(1)
        except KeyboardInterrupt:
            break

def runClient():
    logging.debug("runClient()")
    client = StatusClient(clientStatusCallback)
    client.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)    
    opts, args = getopt.getopt(sys.argv[1:], "", ["client", "server"])
    for opt, arg in opts:
        if opt == "--client":
            runClient()
        elif opt == "--server":
            runServer()                
##    alphabet = string.ascii_letters + string.digits
##    password = ''.join(secrets.choice(alphabet) for i in range(20))
##    print(password)
