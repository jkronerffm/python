from enum import Enum
import logging

class Color(Enum):
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37    
    Grey = 38

class BGColor(Enum):
    Black = 40
    Red = 41
    Green = 42
    Yellow = 43
    Blue = 44
    Magenta = 45
    Cyan = 46
    White = 47
    Grey = 48
    
class Weight(Enum):
    Normal=20
    Bold=1
    
class Colors:
    _initial = "\x1b"
    _reset = "0"
    Reset= f"{_initial}[{_reset}m"

    def __call__(self, color : Color, background : BGColor = BGColor.Black, weight: Weight=Weight.Normal):
        return f"{Colors._initial}[{color.value};{background.value};{weight.value}m"
