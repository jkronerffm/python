import logging
import sys
from pathlib import Path
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk
from threading import Thread
import bluescan
from bluescan import AnyDeviceManager

modulename = Path(__file__).stem
logger = logging.getLogger(modulename)
loggingFormat='%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s %(message)s'

class BluetoothDeviceItem(Gtk.ListBoxRow):
    def __init__(self, parent, name, connected, macAddress):
        super(Gtk.ListBoxRow, self).__init__()
        self._data=macAddress
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 10)
        self.add(box)
        label = Gtk.Label(label=name)
        self.check = Gtk.CheckButton()
        self.check.set_active(connected)
        self.check.connect("toggled", lambda sender: parent.onToggleDevice(sender, macAddress, name))
        box.pack_start(self.check, False, False, 0)
        box.pack_start(label, False, True, 0)

    def __eq__(self, macAddress):
        return self._data == macAddress

    def set_active(self, active = True):
        self.check.set_active(active)
        
class MainWindow(Gtk.Window):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.initUI()
        self.devices = {}
        self.initBackground()

    def doDiscovering(self, manager):
        logger.debug("(manager=%s) enter method" % (str(manager)))
        manager.start_discovery()
        manager.run()
        logger.debug("() leave method")

    def onToggleDevice(self, sender, macAddress, name):
        toggled = sender.get_active()
        logger.debug("(sender=%s, macAddress=%s, toggled=%s)" % (str(sender),macAddress, str(toggled)))
        if macAddress in list(self.devices.keys()):
            device = self.devices[macAddress]
            if toggled:
                device.connect()
            else:
                device.disconnect()

    def onConnectedDevice(self, sender, macAddress, connected, error=""):
        logger.debug("(macAddress=%s, connected=%s, error=%s)" % (macAddress, str(connected), error))
        for index in range (len(self.listbox)):
            row = self.listbox.get_row_at_index(index)
            if macAddress == row:
                row.set_active(connected)
                break
        
    def onDiscoveredDevice(self, sender, macAddress, name, connected):
        myMac = macAddress.replace(':', '-'). casefold()
        if name.casefold() != myMac and not (macAddress in self.devices.keys()):
            self.devices[macAddress] = bluescan.AnyDevice(mac_address=macAddress, manager = self.manager)
            self.devices[macAddress].connectToSignal(self.onConnectedDevice)
            logger.debug("(macAddress=%s, name=%s)" % (macAddress, name))
            row = BluetoothDeviceItem(self, name, connected, macAddress)
            self.listbox.add(row)
            self.listbox.show_all()
        
    def initBackground(self):
        logger.debug("()")
        self.manager = AnyDeviceManager(adapter_name="hci0")
        self.manager.connect("discovered_device", self.onDiscoveredDevice)
        self.thread = Thread(target= self.doDiscovering, args=(self.manager,))
        self.thread.start()
        
    def initUI(self):
        self.builder.add_from_file("bluescanwindow.ui")
        window = self.builder.get_object("main_window")
        self.listbox = self.builder.get_object("device_list")
        window.show_all()
        self.builder.connect_signals(self)

    def onDestroy(self,sender):
        logger.debug("(sender=%s)" % (str(sender)))
        self.manager.stop()
        Gtk.main_quit()

    def onButtonPressed(self, sender):
        logger.debug("(arg=%s)" % (str(sender)))
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=loggingFormat)
    logger.debug("modulename=%s" % (modulename))
    mainWindow = MainWindow()
    Gtk.main()
