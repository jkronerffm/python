import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from common.dictToObj import obj, objFromJson, objToDict
import pigpio
import time
import json
import logging
import threading

class ircontrol:
    def __init__(self, pi, gpio, callback, buttonState = None, timeout=5):
        self.pi = pi
        self.gpio = gpio
        self.code_timeout = timeout
        self.callback = callback
        self.in_code = False
        self._buttonState = buttonState
        
        pi.set_mode(gpio, pigpio.INPUT)
        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cb)

    @staticmethod
    def ReadHashes(filepath):
        irSony = objFromJson(filepath)
        ircontrol.Hashes = objToDict(irSony)

    @staticmethod
    def GetHashKey( value):
        values = list(ircontrol.Hashes.values())
        keys = list(ircontrol.Hashes.keys())
        hashKey = "" if not ircontrol.HasButtonKey(value) else keys[values.index(value)]
        return hashKey

    @staticmethod
    def HasButtonKey(value):
        values = list(ircontrol.Hashes.values())
        return value in values

    @staticmethod
    def AddHashKey(name, value):
        if ircontrol.HasButtonKey(value):
            return
        if name in ircontrol.Hashes:
            return
        ircontrol.Hashes[name] = value

    @staticmethod
    def WriteHashes(filepath):
        with open(filepath, 'w') as f:
            jsonString = json.dumps(ircontrol.Hashes, indent = 4)
            f.write(jsonString)
            f.close()
            
    def _hash(self, old_val, new_val):
        if new_val < (old_val * 0.60):
            val = 13
        elif old_val < (new_val * 0.60):
            val = 23
        else:
            val = 2

        self.hash_val = self.hash_val ^ val
        self.hash_val *= 16777619
        self.hash_val = self.hash_val & ((1<<32)-1)

    def _cb(self, gpio, level, tick):
        if level != pigpio.TIMEOUT:
            if self.in_code == False:
                self.in_code = True
                self.pi.set_watchdog(self.gpio, self.code_timeout)
                self.hash_val = 2166136261
                self.edges = 1
                self.t1 = None
                self.t2 = None
                self.t3 = None
                self.t4 = tick
            else:
                self.edges += 1
                self.t1 = self.t2
                self.t2 = self.t3
                self.t3 = self.t4
                self.t4 = tick
                if self.t1 is not None:
                    d1 = pigpio.tickDiff(self.t1, self.t2)
                    d2 = pigpio.tickDiff(self.t3, self.t4)
                    self._hash(d1, d2)
        else:
            if self.in_code:
                self.in_code = False
                self.pi.set_watchdog(self.gpio, 0)
                if self.edges > 12:
                    self.callback(self.hash_val, self._buttonState)

class ButtonState:
    def __init__(self, buttonDownCallback, buttonPressedCallback):
        self._buttonDownCallback = buttonDownCallback
        self._buttonPressedCallback = buttonPressedCallback
        self._lockButtonDown = threading.Lock()
        self._lockButtonPressed = threading.Lock()
        self._buttonDown = None
        self._buttonPressed = None

    def buttonDown(self):
        result = None
        self._lockButtonDown.acquire()
        result = self._buttonDown
        self._lockButtonDown.release()
        return result

    def setButtonDown(self, value):
        self._lockButtonDown.acquire()
        self._buttonDown = value
        self._lockButtonDown.release()
        
    def buttonPressed(self):
        result = None
        self._lockButtonPressed.acquire()
        result = self._buttonPressed
        self._lockButtonPressed.release()
        return result
        
    def setButtonPressed(self, value):
        self._lockButtonPressed.acquire()
        self._buttonPressed = value
        self._lockButtonPressed.release()

    def _fireButtonDown(self):
        if self._buttonDownCallback != None:
            self._buttonDownCallback(self.buttonDown())

    def _fireButtonPressed(self):
        if self._buttonPressedCallback != None and self.buttonPressed() != None:
            self._buttonPressedCallback(self.buttonPressed())
        self.setButtonPressed(None)
        
    def run(self):
        while True:
            buttonDown = self.buttonDown()
            if buttonDown != None:
                self.setButtonPressed(buttonDown)
                self._fireButtonDown()
            self.setButtonDown(None)
            time.sleep(0.5)
            if self.buttonDown() != self.buttonPressed():
                self._fireButtonPressed()
            
    @staticmethod
    def Run(buttonState):
        buttonState.run()

    @staticmethod
    def Start(buttonDownCallback, buttonPressedCallback):
        buttonState = ButtonState(buttonDownCallback, buttonPressedCallback)
        thread = threading.Thread(target=ButtonState.Run, name="ButtonState", args=[buttonState], daemon=True)
        thread.start()
        return buttonState
    
class LastPressed:
    ButtonCode = 0,
    Ticks = 0
    Timeout = 1
    
    @staticmethod
    def Initialize(buttonCode):
        LastPressed.ButtonCode = buttonCode
        LastPressed.Ticks = time.time()

    @staticmethod
    def HasElapsed():
        return (time.time() - LastPressed.Ticks) > LastPressed.Timeout

    @staticmethod
    def Release():
        LastPressed.ButtonCode = 0
        LastPressed.Ticks = 0

def buttonDown(buttonKey):
    logging.debug(f"buttonDown(buttonKey={buttonKey})")

def buttonPressed(buttonKey):
    logging.debug(f"buttonPressed(buttonKey={buttonKey})")
    if not ircontrol.HasButtonKey(buttonKey):
        name = input(f"please enter the name for value {buttonKey}: ")
        ircontrol.AddHashKey(name, buttonKey)
    else:
        name = ircontrol.GetHashKey(buttonKey)
        print(f"name of buttonkey {buttonKey} is {name}")
    
def callback(buttonKey, buttonState):
    logging.debug(f"callback(buttonKey={buttonKey})")
    if buttonState != None:
        buttonState.setButtonDown(buttonKey)
##    if LastPressed.ButtonCode != buttonKey:
##        LastPressed.Initialize(buttonKey)
##        hashKey = ircontrol.GetHashKey(buttonKey)
##        print("%x" % buttonKey, hashKey)
##    elif LastPressed.HasElapsed():
##        LastPressed.Release()
        

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    rcname = input("Please enter the name of your remote control: ")
    ircontrol.ReadHashes(f"/var/radio/remotecontrol/{rcname}.json")
    pi = pigpio.pi()
    buttonState = ButtonState.Start(buttonDown, buttonPressed)
    
    ircontrol(pi, 17, callback, buttonState = buttonState, timeout=5)
    while True:
        try:
            print(".", end="")
            time.sleep(1)
        except KeyboardInterrupt:
            break
    pi.stop()
    print(ircontrol.Hashes)

