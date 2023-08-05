from AlarmClockBase import Ui_Dialog
from AlarmTime import AlarmTime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QDialog, QMessageBox, QFrame, QListWidgetItem)

class AlarmClock(Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.dialog = None
        self.alarmTimes = []
        self.alarmTime = AlarmTime()
        
    def onClickAdd(self):
        self.alarmTimeList.addItem(QListWidgetItem("new alarm time. Please edit!", type = 0))
        
    def accept(self):
        print("accept: If modified save changings")
        self.dialog.close()

    def reject(self):
        print("reject")
        self.dialog.close()

    def onClickAlarmTimeList(self, item):
        print("clicked alarm time list item(text=%s, type=%d)" % (item.text() , item.type()))
        self.editFrame.show()
        self.alarmTime.setupUi(self.editFrame)
        if (item.type() != 0):
            pass
            
        
    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.dialog = Dialog
        self.toolButton.clicked.connect(self.onClickAdd)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.alarmTimeList.itemClicked.connect(self.onClickAlarmTimeList)
        self.editFrame.hide()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    alarmClock = AlarmClock()
    alarmClock.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
