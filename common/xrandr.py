import subprocess
import logging

class XRandr:
    def __init__(self):
        pass

    def getOutput(self, excludeList = []):
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

    def setBrightness(self, output, value):
        setBrightness = subprocess.run(["xrandr", "--output", output, "--brightness", str(value)], capture_output = True)
        return setBrightness

if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    xrandr = XRandr()
    output = xrandr.getOutput()
    print(output)
    brightness = xrandr.getBrightness(output)
    print(brightness)
    print(xrandr.setBrightness(output, 0.5))
    time.sleep(3)
    xrandr.setBrightness(output,brightness)
