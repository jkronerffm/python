import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def quit(param):
    print("Goodbye world %s" % (param))
    Gtk.main_quit()
    
window = Gtk.Window(title="Hello world")
window.show()
window.connect("destroy", quit)
Gtk.main()
