from PyQt5 import QtCore
from PyQt5.QtCore import QEvent

stringname = {}
for name in vars(QEvent):
    attribute = getattr(QEvent, name)
    if type(attribute) == QEvent.Type:
        stringname[attribute] = name

for val,name in stringname.items():
    print(name,"=", val)

print("======================================================================================")
sortedByVal = dict(sorted(stringname.items(), key = lambda item: item[0]))

for val, name in sortedByVal.items():
    print(name,"=", val)
