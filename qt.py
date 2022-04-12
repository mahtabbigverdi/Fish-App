import sys
from PyQt5.QtWidgets import  *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from ColorWindow import ColorWindow
from Channels import Channels
import cv2
import numpy as np
from Adjustments import Adjustments
from PhotoViewer import PhotoViewer
from Separators import *

class MyWindow(QWidget):
    def __init__(self, channels):
        super(MyWindow, self).__init__()

        self.ALL_COLORS = {}
        self.channels = channels
        self.SELECTED_COLORS = set()

        self.setGeometry(200,200, MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)
        self.main_layout = QHBoxLayout()
        self.setFixedHeight(MAINWINDOW_HEIGHT)
        self.setFixedWidth(MAINWINDOW_WIDTH)

        # main image label
        # self.image_label = QLabel()
        # self.image_label.setGeometry(200,200, IMAGE_WIDTH,IMAGE_HEIGHT)
        # self.image_label.setPixmap(QPixmap(defaultPath).scaled(IMAGE_WIDTH, IMAGE_HEIGHT))
        # self.main_layout.addWidget(self.image_label)
        self.image_vbox = QVBoxLayout()
        self.main_layout.addLayout(self.image_vbox)
        self.viewer = PhotoViewer(self)
        self.image_vbox.addWidget(self.viewer)
        self.viewer.setPhoto(QPixmap("template.jpg").scaled(IMAGE_WIDTH, IMAGE_HEIGHT))
        self.create_zoom()

        self.main_vbox = QVBoxLayout()
        label = QLabel("Channels")
        label.setFixedHeight(50)
        label.setStyleSheet("background-color: gray; font-weight:bold; border-radius: 5px")
        label.setAlignment(Qt.AlignCenter)
        self.main_vbox.addWidget(label)


        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("border:None; background-color:gray; border-radius: 5px")
        self.scroll_widget = QWidget()
        self.check_vbox = QVBoxLayout()
        self.check_vbox.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.check_vbox)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setGeometry(200,200, IMAGE_WIDTH,IMAGE_HEIGHT)
        self.scroll_area.setFixedWidth(IMAGE_WIDTH)
        self.scroll_area.setFixedHeight(IMAGE_HEIGHT)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.main_vbox.addWidget(self.scroll_area)
        self.create_buttons()



        self.main_layout.addLayout(self.main_vbox)
        self.setLayout(self.main_layout)

        self.create_menus()

        self.show()

    def create_zoom(self):
        self.zoom_hbox = QHBoxLayout()
        self.image_vbox.addLayout(self.zoom_hbox)
        self.zoomin_button = QPushButton()
        self.zoomout_button = QPushButton()
        # self.zoomin_button.setIcon(QIcon("icons/zoomin.png"))
        # self.zoomout_button.setIcon(QIcon("icons/zoomout.png"))
        self.zoomin_button.setStyleSheet("border:None; background-image: url('icons/zoomin.png');")
        self.zoomout_button.setStyleSheet("border:None; background-image: url('icons/zoomout.png'); ")
        self.zoomin_button.setFixedWidth(50)
        self.zoomin_button.setFixedHeight(50)
        self.zoomout_button.setFixedHeight(50)
        self.zoomout_button.setFixedWidth(50)
        self.zoomin_button.clicked.connect(lambda : self.viewer.zoomIn())
        self.zoomout_button.clicked.connect(lambda : self.viewer.zoomOut())
        self.zoom_hbox.addWidget(self.zoomin_button)
        self.zoom_hbox.addWidget(self.zoomout_button)


    def create_menus(self):
        self.menubar = QMenuBar()
        self.fileMenu = QMenu("File")
        self.menubar.addMenu(self.fileMenu)
        self.fileMenu.addAction("add channel", self.clicked_btn)

        self.helpMenu = QMenu("help")
        self.menubar.addMenu(self.helpMenu)


        self.main_layout.setMenuBar(self.menubar)

    def create_buttons(self):
        btn1 =  QPushButton("add channel!")
        btn1.setFixedWidth(IMAGE_WIDTH)
        btn1.setFixedHeight(50)
        # btn1.setGeometry(100,100, 150,50)
        btn1.setStyleSheet("background-color: black; color: white;  border-radius: 5px")
        btn1.setIcon(QIcon("icons/icons8-green-plus-64.png"))
        btn1.clicked.connect(self.clicked_btn)
        self.main_vbox.addWidget(btn1)


    def update_checkbox(self, color):
        if color not in self.SELECTED_COLORS:
            self.SELECTED_COLORS.add(color)
            new_hbox = QHBoxLayout()
            check_btn = QToolButton()
            check_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            check_btn.setIcon(QIcon("icons/visibility.png"))
            check_btn.setStyleSheet("border:None")
            check_btn.clicked.connect(lambda : self.check_function(color, check_btn))
            new_hbox.addWidget(check_btn)
            adjust_button = QPushButton(color)
            adjust_button.setStyleSheet("border:None; font-weight:bold")
            adjust_button.setFixedWidth(100)
            adjust_button.setFixedHeight(30)
            adjust_button.clicked.connect(lambda : self.clicked_adjust(color))
            new_hbox.addWidget(adjust_button)
            delete_btn = QToolButton()
            delete_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            delete_btn.setIcon(QIcon("icons/delete.png"))
            delete_btn.setStyleSheet("border:None")
            delete_btn.clicked.connect(lambda : self.delete_channel(new_hbox, color))
            new_hbox.addStretch(8)
            new_hbox.addWidget(delete_btn)
            self.check_vbox.addLayout(new_hbox)

            # Separator = QFrame(self)
            # Separator.setFrameShape(QFrame.HLine)
            # Separator.setFrameShadow(QFrame.Sunken)
            # Separator.setStyleSheet("background-color:blabk;")
            # Separator.setLineWidth(1)
            # self.check_vbox.addWidget(Separator)





        self.update_image()


    def delete_channel(self, hbox, color):
        for i in reversed(range(hbox.count())):
            item = hbox.itemAt(i)

            if isinstance(item, QWidgetItem):
                item.widget().close()

        print(self.check_vbox.children())
        self.SELECTED_COLORS.remove(color)
        self.channels.delete_channel(color)
        self.update_image()

    def clicked_adjust(self, color):
        self.adjust_window = Adjustments(color, self, self.channels)
        self.adjust_window.show()


    def check_function(self, color, btn):
        if color in self.SELECTED_COLORS:
            btn.setIcon(QIcon("icons/hide.png"))
            self.SELECTED_COLORS.remove(color)
        else:
            btn.setIcon(QIcon("icons/visibility.png"))
            self.SELECTED_COLORS.add(color)
        self.update_image()


    def update_image(self):
        img = self.channels.sum_channels(self.SELECTED_COLORS)
        if img.size == 0 :
            pixmap = None
            # self.image_label.setPixmap(pixmap.scaled(IMAGE_WIDTH, IMAGE_HEIGHT))
            self.viewer.setPhoto(None)
        else:
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap(qImg)
            # self.image_label.setPixmap(pixmap.scaled(IMAGE_WIDTH,IMAGE_HEIGHT))
            self.viewer.setPhoto(pixmap)



    def clicked_btn(self):
        image = QFileDialog.getOpenFileName(None, 'OpenFile', '', "*.jpg *.png *.tif *.tiff *.bmp *.JPG")
        imagePath = image[0]
        if imagePath != "":
            self.color_w = ColorWindow(imagePath, self, self.channels)
            self.color_w.show()

app = QApplication(sys.argv)
channels = Channels()
window = MyWindow(channels)
sys.exit(app.exec_())