import os
import re

class FileSelector:
    def __init__(self, basepath, extensions):
        self._basepath = basepath
        self._extensions = extensions

    def select(self, name):
        files = [os.path.join(self._basepath, filename) for filename in os.listdir(self._basepath)]
        pattern = f"(.+(?<=/)){name}\.({'|'.join(self._extensions)})"
        selected = [file for file in files if re.match(pattern, file) != None]
        
        return selected if len(selected) > 1 else selected[0]

if __name__ == "__main__":
    fileSelector = FileSelector(os.path.join(os.getcwd(), '..', 'weather', 'images'), ['jpg', 'png', 'svc'])
    print(fileSelector.select('sun2'))
    print(fileSelector.select('redsun'))
    print(fileSelector.select('moon2'))
