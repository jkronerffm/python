import getopt
import sys

class ArgumentError(Exception):
    def __init__(self, message):
        super().__init__(message)

class FullscreenAndSizeError(ArgumentError):
    def __init__(self):
        super().__init__("You cannot use both arguments --fullscreen and --size!")

class Options:
    opts = "dfhp:s:"
    long_opts = ["debug", "fullscreen", "help", "profile=", "size="]

    def __init__(self):
        self._debug = False
        self._fullscreen = False
        self._profiling = False
        self._statKey = "ncalls"
        self._size = None

    def debug(self):
        return self._debug

    def setDebug(self, value = True):
        self._debug = value
        
    def fullscreen(self):
        return self._fullscreen

    def profiling(self):
        return self._profiling

    def statKey(self):
        return self._statKey
    
    def setFullscreen(self, value = True):
        self._fullscreen = value
        
    def size(self):
        return self._size

    def setProfiling(self, value):
        self._profiling = True
        self._statKey = value if value != "-" else ncalls
        
    def setSize(self, value):
        self._size = value
        
    def printUsage(self, command):
        print(f"{command} [-d|--debug] [-f|--fullscreen] [-h|--help] [-p|--profile] [-s <size>|--size=size]")

    def getOptions(self,command, argv):
        opts, args = getopt.getopt(argv, Options.opts, Options.long_opts)
        for opt, arg in opts:
            if opt in ("-d", "--debug"):
                self.setDebug()
            elif opt in ("-f", "--fullscreen"):
                if self.size() != None:
                    raise FullscreenAndSizeError()
                self.setFullscreen()
            elif opt in ("-h", "--help"):
                self.printUsage(command)
                sys.exit(0)
            elif opt in ("-p", "--profile"):
                self.setProfiling(arg)
            elif opt in ("-s", "--size"):
                if self.fullscreen():
                    raise FullscreenAndSizeError()
                self.setSize(tuple(arg.split("x")))

    @staticmethod
    def Get(command, argv):
        result = Options()
        result.getOptions(command, argv)
        return result

if __name__ == "__main__":
    options = Options.Get(sys.argv[0], sys.argv[1:])
    print(options)
    if options.debug():
        print("debug is set")
    if options.fullscreen():
        print("fullscreen is set")
    if options.size() != None:
        print(f"size={options.size()}")
