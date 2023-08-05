from AlarmOneTimeBase import Ui_Frame

class AlarmOneTime(Ui_Frame):
    def __init__(self):
        super().__init__()

    def onNextTime(self, enable):
        pass

    def onNext(self, enabled):
        self.selectNextComboBox.setEnabled(enabled)
        pass

    def onAtDate(self, enabled):
        self.dateEdit.setEnabled(enabled)
        pass
    
    def onButtonToggled(self, id, checked):
        print("onButtonToggled(id=%d, checked=%d)" % (id,checked))
        options = {
            1: self.onNextTime,
            2: self.onNext,
            3: self.onAtDate
        }
        if (id in options.keys()):
            options[id](checked)
            
    def setupUi(self, Frame):
        super().setupUi(Frame)
        self.buttonGroup.setId(self.nextTimeRadioButton, 1)
        self.buttonGroup.setId(self.nextRadioButton, 2)
        self.buttonGroup.setId(self.atDateRadioButton, 3)
        self.buttonGroup.idToggled.connect(self.onButtonToggled)
