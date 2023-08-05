import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import GObject
import logging

logger = logging.getLogger("testmenu")

class BluesMenu(GObject.Object):
    def __init__(self):
        pass

    def onQuit(self, sender):
        Gtk.main_quit()
        
    def main(self):
        logger.debug("read bluescanmenu.ui")
        builder = Gtk.Builder().new_from_file("bluescanmenu.ui")
        logger.debug("builder=%s" % (str(builder)))
        menu = builder.get_object("blues_menu")
        print(menu)
        iconInfo = Gtk.IconTheme().lookup_icon("bluetooth", 32, Gtk.IconLookupFlags.FORCE_REGULAR)
        icon = iconInfo.load_icon()
        logger.debug("icon is %s" % (iconInfo.get_filename()))
        appIndicator = AppIndicator.Indicator.new("blues",
                                                  iconInfo.get_filename(),
                                                  AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
        appIndicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        appIndicator.set_menu(menu)
        builder.connect_signals(self)
        menu.show_all()
        Gtk.main()

if __name__ == "__main__":        
    logging.basicConfig(level=logging.DEBUG)
    blues = BluesMenu()
    blues.main()
