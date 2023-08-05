import signal
import json
import logging
import os
from urllib.request import Request, urlopen, URLError

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

logger = logging.getLogger('testgi')

APPINDICATOR_ID = '1234567890'

def main():
    logger.debug("()")
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_INFO, appindicator.IndicatorCategory.SYSTEM_SERVICES)
    logger.debug("(indicator=%s)" % (str(indicator)))
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_title("Joke")
    indicator.set_menu(build_menu())
    notify.init(APPINDICATOR_ID)
    gtk.main()

def build_menu():
    logger.debug("()")
    menu = gtk.Menu()
    item_joke = gtk.MenuItem(label='Joke')
    item_joke.connect('activate', joke)
    menu.append(item_joke)
    item_quit = gtk.MenuItem(label='Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def fetch_joke():
    request = Request('http://api.icndb.com/jokes/random?limitTo=[nerdy]')
    response = urlopen(request)
    joke = json.loads(response.read())['value']['joke']
    return joke

def joke(_):
    notify.Notification.new("<b>Joke</b>", fetch_joke(), None).show()

def quit(_):
    logger.debug("")
    notify.uninit()
    gtk.main_quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(asctime)s [%(name)s] [%(filename)s:%(lineno)d] %(funcName)s %(message)s")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

