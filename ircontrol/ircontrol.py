import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from common.dictToObj import obj, objFromJson, objToDict
import pigpio
import time
import json

class ircontrol:
    def __init__(self, pi, gpio, callback, timeout=5):
        self.pi = pi
        self.gpio = gpio
        self.code_timeout = timeout
        self.callback = callback
        self.in_code = False

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
        hashKey = "" if not(value in values) else keys[values.index(value)]
        return hashKey
        
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
                    self.callback(self.hash_val)

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

def callback(hash):
    if LastPressed.ButtonCode != hash:
        LastPressed.Initialize(hash)
        hashKey = ircontrol.GetHashKey(hash)
        print("%x" % hash, hashKey)
    elif LastPressed.HasElapsed():
        LastPressed.Release()
        

if __name__ == "__main__":
    ircontrol.ReadHashes('/var/radio/conf/irsony.json')
    pi = pigpio.pi()
    ircontrol(pi, 17, callback, 5)
    while True:
        try:
            print(".", end="")
            time.sleep(1)
        except KeyboardInterrupt:
            break
    pi.stop()
