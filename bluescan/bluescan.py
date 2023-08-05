import logging
import sys
import gatt
from pathlib import Path
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from threading import Thread
import time

modulename = Path(__file__).stem
logger = logging.getLogger(modulename)
loggingFormat='%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s %(message)s'

class AnyDeviceManager(gatt.DeviceManager, GObject.Object):
    def __init__(self, adapter_name):
        gatt.DeviceManager.__init__(self, adapter_name)
        GObject.GObject.__init__(self)

    def device_discovered(self, device):
        for service in device.services:
            print(dir(service))
        self.emit("discovered_device", device.mac_address, device.alias(), device.is_connected())

class DeviceSignal(GObject.Object):
    def __init__(self):
        super().__init__()

class AnyDevice(gatt.Device):
    def __init__(self, mac_address, manager):
        gatt.Device.__init__(self, mac_address, manager)
        self.signal_sender = DeviceSignal()
        self._name = None
        
    def set_alias(self, value):
        self._name = value

    def alias(self):
        return self._name
    
    def emit(self, mac_address, connected, error=""):
        self.signal_sender.emit("connected_device", mac_address, connected, error)

    def connectToSignal(self, target):
        self.signal_sender.connect("connected_device", target)
        
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))
        self.emit(self.mac_address, True)

    def connect_failed(self, error):
        print("[%s] Connection failed %s" % (self.mac_address, error))
        self.emit(self.mac_address, False, error = error)

    def disconnect_succeeded(self):
        print("[%s] Disconnected" % (self.mac_address))
        self.emit(self.mac_address, False)

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s] Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))
                
    def characteristic_value_updated(self, characteristic, value):
        print("Firmware version:", value.decode("utf-8"))

            
GObject.type_register(AnyDeviceManager)
GObject.signal_new("discovered_device", AnyDeviceManager, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (str, str, bool))
GObject.type_register(DeviceSignal)
GObject.signal_new("connected_device", DeviceSignal, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (str, bool, str))

class Receiver(GObject.Object):
    def __init__(self, sender):
        GObject.GObject.__init__(self)
        self.devices = {}
        sender.connect("discovered_device", self.onDiscoveredDevice)
        
    def onDiscoveredDevice(self, object, mac, name, connected):
        myMac = mac.replace(':', '-'). casefold()
        if name.casefold() != myMac and not (mac in self.devices.keys()):
            self.devices[mac] = name
            print("Discovered [%s] %s (%s)" % ("Connected" if connected else "Disconnected", name, mac))

def threadFunc(manager):
    logger.debug("(manager=%s)"%(str(manager)))
    manager.start_discovery()
    manager.run()
    logger.debug("Leave thread function")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=loggingFormat)
    logger.debug("modulename=%s" % (modulename))
    manager = AnyDeviceManager(adapter_name= 'hci0')
    receiver = Receiver(manager)
    thread = Thread(target = threadFunc, args = { manager })
    thread.start()
    deviceNo = 0;
    while True:
        try:
            if deviceNo < len(receiver.devices):
                mac = list(receiver.devices.keys())[deviceNo]
                deviceNo += 1
                logger.debug("(mac=%s)" % ( mac))
                anyDevice = AnyDevice(mac_address=mac,  manager= manager)
                anyDevice.services_resolved()
                anyDevice.connect()
                time.sleep(5)
                anyDevice.disconnect()
            else:
                deviceNo = 0
        except KeyboardInterrupt:
            print("Caught Ctrl+C")
            break;
                    
    manager.stop()
