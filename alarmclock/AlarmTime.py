from AlarmTimeBase import Ui_Frame
from AlarmOneTime import AlarmOneTime
from AlarmRepeat import AlarmRepeat

class AlarmTime(Ui_Frame):
    def __init__(self):
        super().__init__()
        
    def onClickOneTime(self):
        print("one time")
        self.SettingsFrame2.hide()
        self.SettingsFrame1.show()
        
    def onClickRepeat(self):
        print("repeat")
        self.SettingsFrame1.hide()
        self.SettingsFrame2.show()
        
    def setupUi(self, Frame):
        super().setupUi(Frame)
        self.alarmOneTime = AlarmOneTime()
        self.alarmRepeat = AlarmRepeat()
        self.alarmOneTime.setupUi(self.SettingsFrame1)
        self.alarmRepeat.setupUi(self.SettingsFrame2)
        self.SettingsFrame1.hide()
        self.SettingsFrame2.hide()
        self.oneTimeButton.clicked.connect(self.onClickOneTime)
        self.repeatButton.clicked.connect(self.onClickRepeat)
