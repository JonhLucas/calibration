from lineButtons import lineButtons
from linePoints import linePoints
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QTransform, QPainter, QPixmap, QPen
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread, Qt
import cv2
import time
import numpy as np
import csv

from mouseTracker import MouseTracker
from draggableLabel import draggableLabel
from myButton import myButton

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PyQt5 Media Player")
        self.resize(rect.width(), rect.height())
        self.setMinimumSize(QtCore.QSize(640, 500))

        self.visibilityButton = False
        
        self.backLabel = QtWidgets.QLabel(self)
        self.backLabel.setGeometry(QtCore.QRect(0, 0, rect.width(), rect.height()))
        self.backLabel.setStyleSheet("background-color: darkgray")
        self.backLabel.setObjectName("frontLabel")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")

        self.frontLabel = QtWidgets.QLabel(self.centralwidget)
        self.frontLabel.setGeometry(QtCore.QRect(0, 0, rect.width(), rect.height()))
        self.frontLabel.setObjectName("videoLabel")

        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(110, rect.height() - 80, 340, 20))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        
        #buttons
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)

        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)

        self.check = QtWidgets.QPushButton(self.layoutWidget)
        self.check.setObjectName("check")
        self.horizontalLayout.addWidget(self.check)

        self.clear = QtWidgets.QPushButton(self.centralwidget)
        self.clear.setGeometry(QtCore.QRect(750, rect.height() - 80, 80, 23))
        self.clear.setObjectName("clear")
        self.clear.setText("clear")
        self.clear.setVisible(False)

        self.numMarker = 11
        self.V1 = lineButtons(self.centralwidget)
        self.V1.setup(0, linePoints(self, self.numMarker))


        #self.l2 = linePoints(self, self.numMarker)
        #self.l3 = linePoints(self, self.numMarker)
        #self.l4 = linePoints(self, self.numMarker)

        tracker = MouseTracker(self.frontLabel)
        tracker.positionChanged.connect(self.on_positionChanged)

        self.label_position = QtWidgets.QLabel(self.frontLabel, alignment=QtCore.Qt.AlignCenter)
        self.label_position.setStyleSheet('background-color: lightgreen; border: 1px solid black')
        self.label_position.setObjectName("label_position")

        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(self)

        self.started = False

        self.index = None
        self.keepMarker = False

        self.keepPin = False
        self.focusList = None

        self.dx = 0
        self.dy = 0
        self.frameWidth = rect.width()
        self.frameHeight = rect.height()

        self.frame = None
        self.resolution = [0,0]
        self.getted = []

        #trocar para NoneType
        self.field = None

        #Homography calculated
        self.checked = False

        #Thead
        self.worker = ThreadClass()

        self.setAcceptDrops(True)

        #apagar
        self.drawLines()

    #video 
    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_positionChanged(self, pos):
        a = 30
        b = -15
        if self.frontLabel.geometry().width() < 3*a + pos.x():
            #print(self.backLabel.geometry().width(), a + pos.x(), pos.x() - 2*a)
            a = -(a*2)
        delta = QtCore.QPoint(a, b)
        self.label_position.show()
        self.label_position.move(pos + delta)
        self.label_position.setText("(%d, %d)" % (pos.x() + self.dx, pos.y() + self.dy))
        self.label_position.adjustSize()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.pushButton.setText(_translate("MainWindow", "Open"))
        self.pushButton_2.setText(_translate("MainWindow", "Save"))
        self.pushButton_3.setText(_translate("MainWindow", "Play"))
        self.pushButton_4.setText(_translate("MainWindow", "Restart"))
        self.check.setText(_translate("MainWindow", "Check"))

        #linkar funções
        self.pushButton.clicked.connect(self.loadVideo)
        self.pushButton_3.clicked.connect(self.playPause)
        self.pushButton_4.clicked.connect(self.restart)

        #desabilitar botões
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.check.setEnabled(False)

    def playPause(self):
        if self.started:
            self.started = False
            self.worker.stop()
            self.pushButton_3.setText("Play")
        else:
            self.started = True
            self.worker.start()
            self.pushButton_3.setText("Pause")

    def setPhoto(self, image):
        self.frame = image
        frame = cv2.cvtColor(image[self.dy: self.dy + self.frameHeight, self.dx: self.frameWidth + self.dx, :], cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        #print("setPhoto", frame.shape)
        self.backLabel.setPixmap(QtGui.QPixmap.fromImage(img))

    def restart(self):
        self.worker.kill()
        self.worker.quit()
        if self.filename != "":
            self.started = True
            self.pushButton_3.setText("Pause")
            self.video = cv2.VideoCapture(self.filename)
            ret, frame = self.video.read()
            self.worker.video = self.video
            self.worker.start()

    def loadVideo(self):
        _translate = QtCore.QCoreApplication.translate
        #self.filename = QFileDialog.getOpenFileName(filter="video(*.mp4 *.avi)")[0]

        #self.filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
        self.filename = 'resources/vlc-record-20210410_180547.mp4'
        if self.filename != "":
            if self.started:
                self.started = False
                self.pushButton_3.setText("Play")
            else:
                self.started = True
                self.pushButton_3.setText("Pause")
            self.video = cv2.VideoCapture(self.filename)
            ret, self.frame = self.video.read()
            
            if self.frame.shape[0] < rect.height() or self.frame.shape[1] < rect.width():
                self.frameHeight = self.frame.shape[0]
                self.frameWidth = self.frame.shape[1]
            else:
                self.frameWidth = rect.width()
                self.frameHeight = rect.height()

            self.backLabel.setGeometry(QtCore.QRect(0, 0, self.frameWidth, self.frameHeight))

            self.dx = 0
            self.dy = 0
            self.field = None
            self.frontLabel.clear()

            self.worker.video = self.video
            self.worker.setPhoto = self.setPhoto
            
            try:
                self.worker.start()
            except:
                print("erro ao iniciar Theard de atualização de frames")

            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.check.setEnabled(True)
            if ret:
                self.setPhoto(self.frame)

    def moveMarker(self, a):
       #cleaprint('implement')
       l = self.V1.pins.getMask()
       m = np.array(np.where(l[:,0] == 1), np.int32).T
       #66print(l, m)
       for i in m:
           #print(i[0], a[0], a[1])
           self.V1.pins.list[i[0]].movePin(a[0], a[1])
           '''print(self.dx, self.dy, self.V1.pins.list[i[0]].getPosition())
           self.V1.pins.list[i[0]].movePin(self.dx, self.dy)'''


    #event
    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        position = event.pos()
        (event.source()).drop(position.x(), position.y())
        event.accept()
        (event.source()).setPositionToFrame([position.x() + self.dx, position.y() + self.dy])
        #print("Drop frame coordanates:", (event.source()).getPositionToFrame())
        r = self.V1.getMask()
        #print((event.source()).index)
        if r[0] and r[-1]:
            self.drawLines()
        #print('drop')
  
    def buttonClicked(self, index, button):
        self.keepMarker = True
        self.index = (self.sender()).index
        (self.sender()).setStyleSheet('background-color: red;')

    def mousePressEvent(self, event):
        position = event.pos()
        if self.V1.signal:
            self.V1.signal = False
            self.V1.move(position.x(), position.y())
            #print(self.V1.currentPin)    
            #print(self.V1.getMask())
            r = self.V1.getMask()
            i = self.V1.currentPin
            self.V1.pins.list[i].setPositionToFrame([position.x() + self.dx, position.y() + self.dy])
            #print("frame coordanates:", self.V1.pins.list[i].getPositionToFrame())
            if (i == 0 or i == -1) and r[0] and r[-1]:
                #print('atualizar')
                self.drawLines()
            
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        a = 50
        if self.frame is not None:
            if (a0.key() == QtCore.Qt.Key_6):
                if self.frameWidth + self.dx + a > self.frame.shape[1]:
                    a = self.frame.shape[1] - (self.dx + self.frameWidth)
                self.dx += a
                self.moveMarker([a,0])
                r = self.V1.getMask()
                if r[0] and r[-1]:
                    #print('atualizar linha')
                    self.moveLines()
            elif (a0.key() == QtCore.Qt.Key_4):
                if self.dx - a < 0:
                    a = self.dx
                self.dx -= a
                self.moveMarker([-a,0])
                r = self.V1.getMask()
                if r[0] and r[-1]:
                    #print('atualizar linha')
                    self.moveLines()
            elif (a0.key() == QtCore.Qt.Key_8):
                if self.dy - a < 0:
                    a = self.dy
                self.dy -= a
                self.moveMarker([0, -a])
                r = self.V1.getMask()
                if r[0] and r[-1]:
                    #print('atualizar linha')
                    self.moveLines()
            elif (a0.key() == QtCore.Qt.Key_2):
                if self.frameHeight + self.dy + a > self.frame.shape[0]:
                    a = self.frame.shape[0] - (self.dy + self.frameHeight)
                self.dy += a
                self.moveMarker([0, a])
                r = self.V1.getMask()
                if r[0] and r[-1]:
                    #print('atualizar linha 2')
                    self.moveLines()
            self.setPhoto(self.frame)
        else:
            print("não iniciado")
        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.worker.kill()
        self.worker.quit()
        a0.accept()
        return super().closeEvent(a0)


    #calibration
    def drawLines(self):
        #img = np.zeros((rect.height(), rect.width(), 4), np.int8)
        #Qimg = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGBA8888)
        #pixmap = QtGui.QPixmap.fromImage(self.frontLabel.size())
        pixmap = QtGui.QPixmap(self.frontLabel.size())
        pixmap.fill(Qt.transparent)
        qp = QPainter(pixmap)
        pen = QPen(Qt.red, 2)
        qp.setPen(pen)
        #print(self.V1.pins.begin.getPosition(), self.V1.pins.end.getPosition())
        p1 = self.V1.pins.begin.getPosition()
        p2 = self.V1.pins.end.getPosition()
        qp.drawLine(p1[0], p1[1], p2[0], p2[1])
        qp.end()
        self.frontLabel.setPixmap(pixmap)

    def moveLines(self):
        pixmap = QtGui.QPixmap(self.frontLabel.size())
        pixmap.fill(Qt.transparent)
        qp = QPainter(pixmap)
        pen = QPen(Qt.blue, 2)
        qp.setPen(pen)
        p1 = self.V1.pins.begin.getPosition()
        p2 = self.V1.pins.end.getPosition()
        qp.drawLine(p1[0], p1[1], p2[0], p2[1])
        qp.end()
        self.frontLabel.setPixmap(pixmap)
        

class ThreadClass(QThread):
    video = None
    resize = None
    setPhoto = None
    def run(self):
        a = 0
        self.is_running = True
        while self.video.isOpened() and self.is_running:
            ret, frame = self.video.read()
            if ret:
                self.setPhoto(frame)
                time.sleep(1/30)
            else:
                break

    def stop(self):
        self.is_running = False

    def kill(self):
        self.stop()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    rect = screen.availableGeometry()
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())