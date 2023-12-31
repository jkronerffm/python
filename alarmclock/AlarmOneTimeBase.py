# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AlarmOneTimeBase.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(291, 135)
        Frame.setLineWidth(2)
        self.verticalLayout = QtWidgets.QVBoxLayout(Frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_3 = QtWidgets.QWidget(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 24))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_3.setContentsMargins(9, 0, -1, 0)
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.nextTimeRadioButton = QtWidgets.QRadioButton(self.widget_3)
        self.nextTimeRadioButton.setChecked(True)
        self.nextTimeRadioButton.setObjectName("nextTimeRadioButton")
        self.buttonGroup = QtWidgets.QButtonGroup(Frame)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.nextTimeRadioButton)
        self.horizontalLayout_3.addWidget(self.nextTimeRadioButton)
        self.verticalLayout.addWidget(self.widget_3)
        self.widget = QtWidgets.QWidget(Frame)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 24))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nextRadioButton = QtWidgets.QRadioButton(self.widget)
        self.nextRadioButton.setObjectName("nextRadioButton")
        self.buttonGroup.addButton(self.nextRadioButton)
        self.horizontalLayout.addWidget(self.nextRadioButton)
        self.selectNextComboBox = QtWidgets.QComboBox(self.widget)
        self.selectNextComboBox.setEnabled(False)
        self.selectNextComboBox.setEditable(False)
        self.selectNextComboBox.setObjectName("selectNextComboBox")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.selectNextComboBox.addItem("")
        self.horizontalLayout.addWidget(self.selectNextComboBox)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 24))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.atDateRadioButton = QtWidgets.QRadioButton(self.widget_2)
        self.atDateRadioButton.setObjectName("atDateRadioButton")
        self.buttonGroup.addButton(self.atDateRadioButton)
        self.horizontalLayout_2.addWidget(self.atDateRadioButton)
        self.dateEdit = QtWidgets.QDateEdit(self.widget_2)
        self.dateEdit.setEnabled(False)
        self.dateEdit.setObjectName("dateEdit")
        self.horizontalLayout_2.addWidget(self.dateEdit)
        self.verticalLayout.addWidget(self.widget_2)
        self.timeEdit = QtWidgets.QTimeEdit(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeEdit.sizePolicy().hasHeightForWidth())
        self.timeEdit.setSizePolicy(sizePolicy)
        self.timeEdit.setSizeIncrement(QtCore.QSize(0, 0))
        self.timeEdit.setBaseSize(QtCore.QSize(0, 0))
        self.timeEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.timeEdit.setAutoFillBackground(False)
        self.timeEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.timeEdit.setReadOnly(False)
        self.timeEdit.setObjectName("timeEdit")
        self.verticalLayout.addWidget(self.timeEdit, 0, QtCore.Qt.AlignHCenter)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.nextTimeRadioButton.setText(_translate("Frame", "Next time"))
        self.nextRadioButton.setText(_translate("Frame", "Next"))
        self.selectNextComboBox.setItemText(0, _translate("Frame", "Working day"))
        self.selectNextComboBox.setItemText(1, _translate("Frame", "Sunday"))
        self.selectNextComboBox.setItemText(2, _translate("Frame", "Monday"))
        self.selectNextComboBox.setItemText(3, _translate("Frame", "Tuesday"))
        self.selectNextComboBox.setItemText(4, _translate("Frame", "Wednesday"))
        self.selectNextComboBox.setItemText(5, _translate("Frame", "Thursday"))
        self.selectNextComboBox.setItemText(6, _translate("Frame", "Friday"))
        self.selectNextComboBox.setItemText(7, _translate("Frame", "Saturday"))
        self.atDateRadioButton.setText(_translate("Frame", "at date"))
