import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from Channels import Channels
import cv2
class SelectionWindow(QWidget):
    def __init__(self, main_window, color, label_text, for_adjust = False , for_move = False, for_count = False  ):
        super().__init__()
        self.main_window = main_window
        self.color = color
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setFixedWidth(SELECTIONWINDOW_WIDTH)
        self.setFixedHeight(SELECTIONWINDOW_HEIGHT)
        self.for_adjust = for_adjust
        self.for_move = for_move
        self.for_count = for_count
        image = QLabel()
        image.setPixmap(QPixmap("icons/slider.png").scaled(50,50))
        image.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(image)
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(label)
        self.button_hbox = QHBoxLayout()
        self.main_layout.addLayout(self.button_hbox)
        self.select_button = QPushButton("select a part")
        self.whole_button = QPushButton("select the whole image")
        self.cancel_button = QPushButton("cancel")
        self.select_button.setStyleSheet("border-radius: 3px; background-color:black; color:white; border: 3px solid #4CAF50 ;")
        self.whole_button.setStyleSheet("border-radius: 3px; background-color:black; color:white; border: 3px solid #00BCD4 ;")
        self.cancel_button.setStyleSheet("border-radius: 3px; background-color:black; color:white; border: 3px solid #607D8B ;")
        self.select_button.setFixedWidth(130)
        self.select_button.setFixedHeight(30)
        self.whole_button.setFixedWidth(160)
        self.whole_button.setFixedHeight(30)
        self.cancel_button.setFixedWidth(130)
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.clicked.connect(lambda : self.close())
        self.whole_button.clicked.connect(self.select_whole)
        self.select_button.clicked.connect(self.select_part)
        self.button_hbox.addWidget(self.cancel_button)
        self.button_hbox.addWidget(self.whole_button)
        self.button_hbox.addWidget(self.select_button)


    def select_whole(self):
        if self.for_adjust:
            self.main_window.open_adjust(self.color,0,0, IMAGE_WIDTH, IMAGE_HEIGHT)
        elif self.for_move:
            self.main_window.move_whole_func(self.color)
        elif self.for_count:
            self.main_window.open_count(self.color,0,0, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.close()

    def select_part(self):
        if self.for_adjust:
            self.main_window.switch_adjust(self.color)
        elif self.for_move:
            self.main_window.switch_move(self.color)
        elif self.for_count:
           self.main_window.switch_count(self.color)

        self.close()

