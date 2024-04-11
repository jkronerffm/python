import subprocess
import logging


class XRandr:
    def __init__(self):
        pass

    def getName(self, excludeList = []):
        xrandr_process = subprocess.Popen(["xrandr", "-q"], stdout = subprocess.PIPE, text = True)
        grep_process = subprocess.Popen(["grep", "connected"], stdin = xrandr_process.stdout,
                                        stdout = subprocess.PIPE, text = True)

        output, error = grep_process.communicate()
        logging.debug(f"getDisplay(output={output})")
        output_list = output.split()
        display = None
        for idx, word in enumerate(output_list):
            if word == "connected":
                prev_word = output_list[idx-1]
                if not (prev_word in excludeList):
                    display = prev_word
                    break
        return display

    def getOutput(self, excludeList = []):
        return self.getName(excludeList)
    
    def getBrightness(self, output):
        xrandr_process = subprocess.Popen(["xrandr", "--verbose"],
                                          stdout = subprocess.PIPE,
                                          text = True)
        grep_process = subprocess.Popen(["grep", "-C5", "-i", output],
                                        stdin = xrandr_process.stdout,
                                        stdout = subprocess.PIPE,
                                        text = True)

        output, error = grep_process.communicate()
        output_list = output.split('\n')
        logging.debug(f"getBrightness(output_list={output_list})")
        brightness = None
        for line in output_list:
            if "Brightness" in line:
                brightness = float(line.split(':')[1])
                break

        return brightness

    def switch(self, output, on = True):
        cmd = "--auto" if on else "--off"
        sbr = subprocess.run(["xrandr", "--output", output, cmd], capture_output = True)
        return sbr
    
    def switchOff(self, output):
        return switch(output, False)
    
    def switchOn(self, output):
        return switch(output, True)
    
    def setBrightness(self, output, value):
        setBrightness = subprocess.run(["xrandr", "--output", output, "--brightness", str(value)], capture_output = True)
        return setBrightness

if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    xrandr = XRandr()
    name = xrandr.getName()
    print(name)
    brightness = xrandr.getBrightness(name)
    print(brightness)
    print(xrandr.setBrightness(name, 0.5))
    time.sleep(3)
    xrandr.setBrightness(name,brightness)
    time.sleep(3)
    print(xrandr.switchOff(name))
    time.sleep(3)
    print(xrandr.switchOn(name))
    time.sleep(3)
    print(xrandr.switch(name, True))
    time.sleep(3)
    print(xrandr.switch(name, False))
