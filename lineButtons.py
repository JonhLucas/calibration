from linePoints import linePoints
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
class lineButtons(QtWidgets.QWidget):
    header = None
    begin= None
    mid = None
    end = None
    horizontalLayout = None
    pins = None
    visible = True
    currentPin = 0
    counter = 0
    signal = False

    def setup(self, index, pins : linePoints):
        self.setGeometry(QtCore.QRect(100 * index + 10, 10, 50, 110))
        self.setObjectName("LayoutWidget1")
        self.horizontalLayout = QtWidgets.QVBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout1")

        self.header = QtWidgets.QPushButton(self)
        self.header.setObjectName("L" + str(index))
        self.header.setText("L" +  str(index))
        self.header.clicked.connect(self.enable)
        self.horizontalLayout.addWidget(self.header)

        self.begin = QtWidgets.QPushButton(self)
        self.begin.setObjectName("begin")
        self.begin.setText("begin")
        self.begin.setVisible(self.visible)
        self.horizontalLayout.addWidget(self.begin)

        self.mid = QtWidgets.QPushButton(self)
        self.mid.setObjectName("mid")
        self.mid.setText("middle")
        self.mid.setVisible(self.visible)
        self.horizontalLayout.addWidget(self.mid)

        self.end = QtWidgets.QPushButton(self)
        self.end.setObjectName("end")
        self.end.setText("end")
        self.end.setVisible(self.visible)
        self.horizontalLayout.addWidget(self.end)

        self.pins = pins

        self.begin.clicked.connect(self.setBegin)
        self.mid.clicked.connect(self.setMid)
        self.end.clicked.connect(self.setEnd)

    def setBegin(self):
        self.currentPin = 0
        self.signal = True

    def setEnd(self):
        self.currentPin = -1
        self.signal = True

    def setMid(self):
        if self.counter < self.pins.size - 2:
            self.counter += 1
        self.currentPin = self.counter
        self.signal = True

    def enable(self):
        self.visible = ~self.visible
        self.begin.setVisible(self.visible)
        self.mid.setVisible(self.visible)
        self.end.setVisible(self.visible)
    
    def move(self, x, y):
        self.pins.list[self.currentPin].drop(x, y)
        self.pins.mask[self.currentPin] = 1
    
    def getMask(self):
        return self.pins.mask
