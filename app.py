from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox
from mriui import Ui_MainWindow
from phantom import phantom
import numpy as np
import qimage2ndarray
import sys

MAX_CONTRAST = 2
MIN_CONTRAST = 0.1
MAX_BRIGHTNESS = 100
MIN_BRIGHTNESS = -100
SAFETY_MARGIN = 10
MAX_PIXELS_CLICKED = 3


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Actions
        self.ui.comboSheppSize.currentTextChanged.connect(self.showPhantom)
        self.ui.comboViewMode.currentTextChanged.connect(self.changePhantomMode)

        # Mouse Events
        self.ui.phantomlbl.setMouseTracking(False)
        self.ui.phantomlbl.mouseMoveEvent = self.editContrastAndBrightness

        # Scaling
        self.ui.phantomlbl.setScaledContents(True)

        # initialization
        self.qimg = None
        self.img = None
        self.originalPhantom = None
        self.PD = None
        self.T1 = None
        self.T2 = None
        self.phantomSize = 512

        self.FA = 90
        self.cosFA = 0
        self.sinFA = 1
        self.TE = 0.001
        self.TR = 0.5
        self.x = 0
        self.y = 0

        self.pixelsClicked = [(0, 0), (0, 0), (0, 0)]
        self.pixelSelector = 0

        # For Mouse moving, changing Brightness and Contrast
        self.lastY = None
        self.lastX = None

        # For Contrast Control
        self.contrast = 1.0
        self.brightness = 0


    def showPhantom(self, value):
        size = int(value)
        self.phantomSize = size
        img = phantom(size)
        img = img * 255
        self.img = img
        self.PD = img
        self.T1 = phantom(size, 'T1')
        self.T2 = phantom(size, 'T2')
        self.originalPhantom = img
        self.pixelsClicked = [(0, 0), [0, 0], [0, 0]]
        self.showPhantomImage()
        self.ui.comboViewMode.setCurrentIndex(0)

    def showPhantomImage(self):
        self.qimg = qimage2ndarray.array2qimage(self.img)
        self.ui.phantomlbl.setPixmap(QPixmap(self.qimg))

    def changePhantomMode(self, value):

        if value == "PD":
            self.img = self.PD
        if value == "T1":
            self.img = self.T1
        if value == "T2":
            self.img = self.T2

        self.img = self.img * (255 / np.max(self.img))
        self.originalPhantom = self.img
        self.showPhantomImage()

    def editContrastAndBrightness(self, event):
        if self.lastX is None:
            self.lastX = event.pos().x()
        if self.lastY is None:
            self.lastY = event.pos().y()
            return

        currentPositionX = event.pos().x()
        if currentPositionX - SAFETY_MARGIN > self.lastX:
            self.contrast += 0.01
        elif currentPositionX < self.lastX - SAFETY_MARGIN:
            self.contrast -= 0.01

        currentPositionY = event.pos().y()
        if currentPositionY - SAFETY_MARGIN > self.lastY:
            self.brightness += 1
        elif currentPositionY < self.lastY - SAFETY_MARGIN:
            self.brightness -= 1
        # Sanity Check
        if self.contrast > MAX_CONTRAST:
            self.contrast = MAX_CONTRAST
        elif self.contrast < MIN_CONTRAST:
            self.contrast = MIN_CONTRAST
        if self.brightness > MAX_BRIGHTNESS:
            self.brightness = MAX_BRIGHTNESS
        elif self.brightness < MIN_BRIGHTNESS:
            self.brightness = MIN_BRIGHTNESS

        self.img = 128 + self.contrast * (self.originalPhantom - 128)
        self.img = np.clip(self.img, 0, 255)

        self.img = self.img + self.brightness
        self.img = np.clip(self.img, 0, 255)
        self.showPhantomImage()

        self.lastY = currentPositionY
        self.lastX = currentPositionX


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
