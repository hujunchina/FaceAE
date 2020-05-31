import sys
from numpy import asarray
from face_ae_const import CONST_VAL
from cv2 import cvtColor, COLOR_RGB2BGR
from PIL import (ImageQt)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QFormLayout, QGridLayout, QLineEdit, QPushButton,QFileDialog)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import (Qt, QRect, pyqtSignal)
GLOBAL_VAL = {
    'isDraw': False
}

# 自定义显示图片的窗口，并实现鼠标拖动截图
class ImgPanel(QLabel):
# 1. 定义个信号 signal
    mouseReleased = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.isPaint = False
        self.checkDraw()

    def mousePressEvent(self, event):
        self.checkDraw()
        self.isPaint = True
        self.x0 = event.x()
        self.y0 = event.y()

# 图片的更新和对图片的处理入口
    def mouseReleaseEvent(self, event):
        self.checkDraw()
        self.clearRect()
        self.img_cut = self.pixmap().copy(self.rect)
        self.setPixmap(self.img_cut)
        self.setAlignment(Qt.AlignCenter)
        # screen = QApplication.primaryScreen()
        # if screen is not None:
        #     self.img_screen = screen.grabWindow(0, self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
        # self.setPixmap(self.img_screen)
        # self.setScaledContents(False)
        img_pil = ImageQt.fromqpixmap(self.pixmap())  # qpixmap to image
        img_cv = cvtColor(asarray(img_pil), COLOR_RGB2BGR) # image to cv2
# 2 在需要的地方发射就行了
        self.mouseReleased.emit([img_cv.mean()])

    def mouseMoveEvent(self, event):
        self.checkDraw()
        if self.isPaint:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.checkDraw()
        self.rect = QRect(self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
        painter = QPainter(self)

        painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
        painter.drawRect(self.rect)

    def clearRect(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.isPaint = False
        GLOBAL_VAL['isDraw'] = False
        self.update()

    def checkDraw(self):
        if GLOBAL_VAL['isDraw'] is False:
            self.isPaint = False
            pass


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(CONST_VAL['WIN_TITLE'])
        self.resize(CONST_VAL['WIN_W'], CONST_VAL['WIN_H'])
        self.move(CONST_VAL['INIT_POSITION_Y'], CONST_VAL['INIT_POSITION_X'])
        self.init_layout()
        self.img_url_val = None

    def init_layout(self):
        self.grid = QGridLayout()
        self.img_url = QLineEdit()
        self.img_open_btn = QPushButton(CONST_VAL['OPEN_IMG'])
        self.img_open_btn.clicked.connect(self.open_file_slot)
        self.img_lbl = ImgPanel()
        self.img_lbl.mouseReleased.connect(self.img_info_slot)
        self.img_lbl.setFixedHeight(CONST_VAL['IMG_MAX_H'])
        self.img_lbl.setFixedWidth(CONST_VAL['IMG_MAX_W'])
        self.img_reset_btn = QPushButton(CONST_VAL['RESET_IMG'], self.img_lbl)
        self.img_reset_btn.clicked.connect(self.img_reset_slot)
        self.right_lbl = QLabel()
        self.img_info_hbox = QFormLayout(self.right_lbl)
        # self.img_info_hbox.setSpacing(20)
# 添加布局
        self.grid.addWidget(self.img_url, 0, 0, 1, 3)
        self.grid.addWidget(self.img_open_btn, 0, 3, 1, 1)
        self.grid.addWidget(self.img_lbl, 1, 0, 3, 3)
        self.grid.addWidget(self.right_lbl, 1, 3, 3, 1)

# 设置右边图像信息布局
        self.img_mean_lbl = QLineEdit("00000")
        self.img_info_hbox.addRow(CONST_VAL['MEAN_TXT'], self.img_mean_lbl)
        self.img_info_hbox.addRow(CONST_VAL['CLEAR_TXT'], QLineEdit("00000"))
        self.img_info_hbox.addRow(CONST_VAL['BALANCE_TXT'], QLineEdit("00000"))
        self.setLayout(self.grid)

    def img_info_slot(self, data):
        mean_msg = "{:.5f}".format(data[0])
        self.img_mean_lbl.setText(mean_msg)

# 图片打开按钮响应方法
    def open_file_slot(self):
        GLOBAL_VAL['isDraw'] = True
        img_name = QFileDialog.getOpenFileName(self, CONST_VAL['OPEN_IMG'], CONST_VAL['OPEN_IMG_START_FOLD'])
        self.img_url.setText(img_name[0])
        self.img_url_val = img_name[0]
        print(img_name[0])
        if img_name[0]:
            img_pixmap = QPixmap(img_name[0])
            ratio = CONST_VAL['IMG_MAX_W'] / img_pixmap.width()
            img_resize = img_pixmap.scaled(img_pixmap.width() * ratio, img_pixmap.height() * ratio)
            self.img_lbl.setPixmap(img_resize)
            self.img_lbl.setAlignment(Qt.AlignLeft)
            # self.img_lbl.setScaledContents(True)

# 图片重置按钮响应方法
    def img_reset_slot(self):
        GLOBAL_VAL['isDraw'] = True
        if self.img_url_val:
            self.img_url_val = self.img_url_val
            img_pixmap = QPixmap(self.img_url_val)
            ratio = CONST_VAL['IMG_MAX_W'] / img_pixmap.width()
            img_resize = img_pixmap.scaled(img_pixmap.width() * ratio, img_pixmap.height() * ratio)
            self.img_lbl.setPixmap(img_resize)
            self.img_lbl.setAlignment(Qt.AlignLeft)
            # self.img_lbl.setScaledContents(True)
        else:
            self.open_file_slot()
