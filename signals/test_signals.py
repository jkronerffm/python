import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GObject

class Sender(GObject.Object):
    def __init__(self):
        GObject.GObject.__init__(self)


GObject.type_register(Sender)
GObject.signal_new("x_signal", Sender, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (str,str))

class Receiver(GObject.Object):
    def __init__(self, sender, signalname):
        GObject.GObject.__init__(self)
        self.signalname = signalname
        sender.connect(signalname, self.report_signal)

    def report_signal(self, sender, data1, data2):
        print("Receiver reacts to %s -> data1=%s, data2=%s" % (self.signalname,data1, data2))

def user_callback(object, data1, data2):
    print("object=%s, data1=%s, data2=%s" % (str(type(object)),data1, data2))
    print("user callback to x_signal")

class Sender2(GObject.Object):
    __gsignals__ = {
        "x1_signal": (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, (str,str))
    }

    def __init__(self):
        GObject.GObject.__init__(self)

GObject.type_register(Sender2)

if __name__ == '__main__':
    sender = Sender()
    receiver = Receiver(sender, "x_signal")

    sender.connect("x_signal", user_callback)
    sender.emit("x_signal", "MAC-Address", "Name")

    sender2 = Sender2()
    receiver = Receiver(sender2, "x1_signal")
    sender2.connect("x1_signal", user_callback)
    sender2.emit("x1_signal", "MAC-Address", "Name")

