import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Gtk
from gi.repository import GObject
import bluescan
from bluescan import AnyDeviceManager
from pathlib import Path
import logging
from threading import Thread

AppIndicator_ID = 'Bluetooth_menu'
modulename = Path(__file__).stem
logger = logging.getLogger(modulename)
loggingFormat='%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s %(message)s'

class BluetoothDeviceMenuItem(Gtk.CheckMenuItem):
    def __init__(self, parent, device, connected):
        super().__init__(label = device.alias())
        self._parent = parent
        self._macAddress = device.mac_address
        self.set_active(connected)
        logger.debug("(%s)" % (str(self)))
        
    def __str__(self):
        return "mac_address=%s, name=%s, connected=%s" % (self._macAddress, self.get_label(), str(self.get_active()))

    def onToggleDevice(self, sender):
        logger.debug("(%s)" % (str(self)))
        if (self._parent != None):
            self._parent.onToggledDevice(self._macAddress, self.get_active())
        
class BluetoothMenu(GObject.Object):
    def __init__(self):
        self.devices = {}

    def onConnectedDevice(self, sender, macAddress, connected, error=""):
        logger.debug("(macAddress=%s, connected=%s)" % (macAddress, str(connected)))
        pass

    def onToggledDevice(self, macAddress, active):
        logger.debug("(macAddress=%s, active=%s)" % (macAddress, str(active)))
        if active:
            self.devices[macAddress].connect()
        else:
            self.devices[macAddress].disconnect()
        
    def onDiscoveredDevice(self, sender, macAddress, name, connected):
        myMac = macAddress.replace(':', '-'). casefold()
        if name.casefold() != myMac and not (macAddress in list(self.devices.keys())):
            device = bluescan.AnyDevice(mac_address=macAddress, manager = self.manager)
            self.devices[macAddress] = device
            device.set_alias(name)
            device.connectToSignal(self.onConnectedDevice)
            logger.debug("(macAddress=%s, name=%s)" % (macAddress, name))
            if self.devicesMenu != None:
                if len(self.devicesMenu) == 1:
                    menuItem = self.devicesMenu.get_children()[0]
                    if menuItem.get_label() == 'Dummy':
                        logger.debug("(): remove dummy menu item")
                        self.devicesMenu.remove(menuItem)
                menuItem = BluetoothDeviceMenuItem(self, device, connected)
                self.devicesMenu.append(menuItem)
                self.devicesMenu.show_all()
            
    def main(self):
        iconInfo = Gtk.IconTheme().lookup_icon("bluetooth", 32, Gtk.IconLookupFlags.FORCE_REGULAR)
        icon = iconInfo.load_icon()
        indicator = AppIndicator.Indicator.new(AppIndicator_ID, iconInfo.get_filename(), AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.buildMenu())
        self.initBackground()
        Gtk.main()

    def doDiscovering(self, manager):
        manager.start_discovery()
        manager.run()
        
    def initBackground(self):
        self.manager = AnyDeviceManager(adapter_name="hci0")
        self.manager.connect("discovered_device", self.onDiscoveredDevice)
        self.thread = Thread(target= self.doDiscovering, args=(self.manager,))
        self.thread.start()

    def quit(self,_):
        Gtk.main_quit()
        
    def buildMenu(self):
        menu = Gtk.Menu()
        item = Gtk.MenuItem(label = "Devices")
        self.devicesMenu = Gtk.Menu()
        dummy = Gtk.MenuItem(label = "Dummy")
        item.set_submenu(self.devicesMenu)
        menu.append(item)
        self.devicesMenu.append(dummy)
        quitItem = Gtk.MenuItem(label = "Quit")
        quitItem.connect("activate", self.quit)
        menu.append(quitItem)
        menu.show_all()

        return menu

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=loggingFormat)
    logger.debug("modulename=%s" % (modulename))
    bluetoothMenu = BluetoothMenu()
    bluetoothMenu.main()
