import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
gi.require_version("Notify", '0.7')
from gi.repository import GObject as gobject
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GLib as glib
import logging
from googletrans import Translator as gTrans

logger = logging.getLogger('translator')

APPINDICATOR_ID = 'translator'
LOGFORMAT = "[%(levelname)s] %(asctime)s) [%(name)s] [%(filename)s:%(lineno)d] %(funcName)s %(message)s"

class TranslatorWindow(gtk.Window):
    WindowTimeout = 30
    
    def __init__(self):
        super().__init__(title="Translator")
        self.initUI()

    def initUI(self):
        self.set_decorated(False)
        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=6)
        hbox = gtk.Box(spacing=6)
        self.add(vbox)
        self.input_entry = gtk.Entry()
        self.button = gtk.Button(label="Translate")
        self.button.connect("clicked", self.translate)
        self.output_entry = gtk.Entry()
        hbox.pack_start(self.input_entry, True, True, 0)
        hbox.pack_start(self.button, True, True, 0)
        vbox.pack_start(hbox, True, True, 0)
        vbox.pack_start(self.output_entry, True, True, 0)
        glib.timeout_add_seconds(TranslatorWindow.WindowTimeout, self.timer_callback)

    def translate(self, _):
        text = self.input_entry.get_text()
        logger.debug("(text=%s)" % (text))
        notify.init('Translator')
        translator = gTrans()
        translation = translator.translate(text=text)
        logger.debug("(translation=%s)" % translation)
        notification = notify.Notification.new("Translation", translation.text)
        notification.set_timeout(notify.EXPIRES_NEVER)
        notification.add_action('quit', 'Quit', self.close)
        notification.show()
                
    def timer_callback(self):
        logger.debug("(): %d seconds are gone" % (TranslatorWindow.WindowTimeout))
        self.close()
        
class Translator:
    def __init__(self):
        self._builder = None

    def main(self):
        logger.debug("")
        indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_INFO, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.buildMenu())
        notify.init(APPINDICATOR_ID)
        gtk.main()

    def buildMenu(self):
        logger.debug("")
        menu = gtk.Menu()
        itemTranslate = gtk.MenuItem(label="Translate")
        itemTranslate.connect("activate", self.translate)
        menu.append(itemTranslate)
        itemQuit = gtk.MenuItem(label="Quit")
        itemQuit.connect("activate", self.quit)
        menu.append(itemQuit)
        menu.show_all()
        return menu

    def getMousePosition(self, widget):
        device = widget.get_display().get_default_seat().get_pointer()
        window = gtk.Window.get_root_window(widget)
        (_, x, y, mask) = window.get_device_position(device)
        return (x,y)
        
    def translate(self, menuItem):
        logger.debug("()")
        (x,y) = self.getMousePosition(menuItem)
        logger.debug("x=%d, y=%d)" % (x,y))
        
        self.window = TranslatorWindow()
        (width, height) = self.window.get_size()
        xWin = x - width
        yWin = y
        self.window.move(xWin, yWin)
        self.window.show_all()

    def quit(self, _):
        logger.debug("")
        notify.uninit()
        gtk.main_quit()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG,
                        format= LOGFORMAT)
    translator = Translator()
    translator.main()
    
        
