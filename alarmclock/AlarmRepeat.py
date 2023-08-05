from AlarmRepeatBase import Ui_Frame
from PyQt5 import QtWidgets, QtGui

class AlarmRepeat(Ui_Frame):
    def __init__(self):
        super().__init__()

    def onEveryDay(self, checked):
        if (not checked):
            return

        self.daysBox.setEnabled(False)
        self.enableDays(False)
        self.checkDays(range(1,8), False)

    def enableDays(self, enabled = True):
        for day in range(1,8):
            checkbox = self.dayGroup.button(day)
            if (checkbox == None):
                raise Exception("Checkbox not found")
            checkbox.setEnabled(enabled)
            
    def checkDays(self, days, checked):
        for day in days:
            checkbox = self.dayGroup.button(day)
            if (checkbox == None):
                raise Exception('Checkbox not found')
            checkbox.setChecked(checked)
            
    def onEveryWorkingDay(self, checked):
        if (not checked):
            return

        self.daysBox.setEnabled(False)
        self.enableDays(False)
        self.checkDays(range(2,7), True)

    def onEvery(self, checked):
        if (not checked):
            return

        self.daysBox.setEnabled(True)
        self.enableDays()
        
    def onButtonToggled(self, id, checked):
        options = {
            1: self.onEveryDay,
            2: self.onEveryWorkingDay,
            3: self.onEvery
        }
        if id in options.keys():
            options[id](checked)

    def onDayToggled(self, id, checked):
        pass
    
    def setupUi(self, Frame):
        super().setupUi(Frame)
        self.dayGroup.setExclusive(False)
        self.buttonGroup.setId(self.everyDayRadioButton, 1)
        self.buttonGroup.setId(self.everyWorkingDayRadioButton, 2)
        self.buttonGroup.setId(self.everyRadioButton, 3)
        for i in range(1,8):
            checkbox = self.daysBox.findChild(QtWidgets.QCheckBox, "Checkbox%d" % i)
            if (checkbox == None):
                raise Exception("Control Checkbox%d not found" % i)
            self.dayGroup.setId(checkbox, i)
        self.buttonGroup.idToggled.connect(self.onButtonToggled)
        self.dayGroup.idToggled.connect(self.onDayToggled)
