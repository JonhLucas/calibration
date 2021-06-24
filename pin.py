from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QDrag, QPixmap, QPainter
from PyQt5.QtCore import *
from PyQt5.QtCore import QMimeData, Qt

class pinLabel(QLabel):
    index = 0
    x = 0
    y = 0
    dx = 13
    dy = 50
    frameCoordanate = [0,0]

    def setup(self, index):
        self.index = index
        self.setGeometry(QtCore.QRect(0, 0, self.dx * 2, self.dy))
        self.x = index * 100 
        self.y = 200
        self.move(self.x - self.dx, self.y - self.dy)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setText(str(self.index))
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setStyleSheet("border-image: url(resources/pin.png);")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mimedata = QMimeData()
            mimedata.setText(self.text())
            drag.setMimeData(mimedata)
            pixmap = QPixmap(self.size())
            painter = QPainter(pixmap)
            painter.drawPixmap(self.rect(), self.grab())
            painter.end()
            drag.setPixmap(pixmap)
            drag.setHotSpot(QtCore.QPoint(self.dx, self.dy))
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def drop(self, x, y):
        self.move(x - self.dx, y - self.dy)
        self.x = x
        self.y = y

    def movePin(self, x, y):
        self.drop(self.x - x, self.y - y)
        #self.move(self.x - x - self.dx, self.y - y - self.dy)

    def getPosition(self):
        return [self.x, self.y]

    def getPositionToFrame(self):
        return self.frameCoordanate

    def setPositionToFrame(self, a):
        self.frameCoordanate = a

    def releaseMouseEvent(self, event):
        return super(pinLabel, self).releaseMouseEvent(event)
