import os
import json
import pygame
from  pygame.font import SysFont

class FontFactory:
    FontDefinitionPath = "/var/radio/conf/Fonts.json"
    
    Instance = None
    
    def __init__(self):
        self._fontData = None

    @classmethod
    def Get(cls):
        if cls.Instance == None:
            cls.Instance = cls()
            cls.Instance._load(cls.FontDefinitionPath)
        return cls.Instance

    def _load(self,filepath):
        with open(filepath, "r") as jsonFile:
            self._fontData = json.load(jsonFile)
            jsonFile.close

    def __len__(self):
        return len(self._jsonData)

    @property
    def fonts(self):
        return self._fontData
    
    def __getitem__(self, key):
        if self.fonts == None or not key in self.fonts:
            raise KeyError(f"key {key} is not in FontFactory")

        font = self.fonts[key]
        return SysFont(font['name'], font['size'], font['bold'], font['italic'])
                    
if __name__ == "__main__":
    pygame.init()
    FontFactory.FontDefinitionPath = "./fonts.json"
    fontFactory = FontFactory.Get()
    font = fontFactory['arial14']
    print(font)
    pygame.quit()
