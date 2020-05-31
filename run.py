import sys
from numpy import asarray
from PyQt5.QtWidgets import (QApplication)
import face_ae_window

app = QApplication(sys.argv)
win = face_ae_window.MainWindow()
win.show()
sys.exit(app.exec())