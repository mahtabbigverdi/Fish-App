import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from CountViewer import CountViewer
import numpy as np
import cv2
class WholeCountWindow(QWidget):
    def __init__(self, main_window, channels, image, SELECTED_COLORS ):
        super().__init__()
        self.main_window = main_window
        self.crops = []
        self.SELECTED_COLORS = SELECTED_COLORS
        self.image = image
        self.mask_mode = False
        self.image_height = self.image.shape[0]
        self.image_width = self.image.shape[1]
        self.channels = channels
        self.masked_image = np.zeros_like(self.image)
        self.mask = np.ones_like(self.image).astype(np.uint8)
        self.setup_bool = False
        self.main_layout = QHBoxLayout()

        self.setLayout(self.main_layout)
        self.setFixedWidth(WHOLE_COUNTWINDOW_WIDTH)
        self.setFixedHeight(WHOLE_COUNTWINDOW_HEIGHT)
        ## the viewer for image in count window
        self.viewer = CountViewer(self, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.viewer.setPhoto(None)
        self.viewer.counter_mode = True
        self.main_layout.addWidget(self.viewer)
        self.main_vbox = QVBoxLayout()
        self.main_vbox.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.main_vbox)
        self.buttonGroup = QButtonGroup()


        self.create_add_button()
        self.create_undo_button()
        self.create_mask_button()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(200)
        self.label.setStyleSheet("font-weight:bold; color:black; font-size:20px; border:4px solid black; border-radius: 2px")
        self.main_vbox.addWidget(self.label)

        self.create_close_button()


        ## find contours and blobs
        # self.process_image()
        ## draw contours and their numbers
        self.show_image()
        self.update_count()

    def create_mask_button(self):
        self.mask_button = QPushButton("Mask")
        self.mask_button.setFixedWidth(200)
        self.mask_button.setFixedHeight(50)
        self.mask_button.setStyleSheet("background-color: black; color: white;  border-radius: 5px; font-weight: bold")
        self.buttonGroup.addButton(self.mask_button)
        self.mask_button.clicked.connect(self.mask_func)
        self.main_vbox.addWidget(self.mask_button)

    def create_undo_button(self):
        self.undo_button = QPushButton("  Undo selection")
        self.undo_button.setFixedWidth(200)
        self.undo_button.setFixedHeight(50)
        self.undo_button.setIcon(QIcon("icons/negative.png"))
        self.undo_button.setStyleSheet("background-color:  #e31773; color: white;  border-radius: 5px; font-weight: bold")
        self.buttonGroup.addButton(self.undo_button)
        self.undo_button.clicked.connect(self.undo_func)
        self.main_vbox.addWidget(self.undo_button)

    def create_add_button(self):
        self.add_button = QPushButton("  Add selection!")
        self.add_button.setFixedWidth(200)
        self.add_button.setFixedHeight(50)
        self.add_button.setStyleSheet("background-color: #009688; color: white;  border-radius: 5px; font-weight: bold")
        self.add_button.setIcon(QIcon("icons/plus.png"))
        self.buttonGroup.addButton(self.add_button)
        self.add_button.clicked.connect(self.add_func)
        self.main_vbox.addWidget(self.add_button)

    def create_close_button(self):
        self.close_button = QPushButton("Close")
        self.close_button.setFixedWidth(200)
        self.close_button.setFixedHeight(50)
        self.close_button.setStyleSheet("background-color: #86d1c5; color: white;  border-radius: 5px; font-weight: bold")
        self.buttonGroup.addButton(self.close_button)
        self.close_button.clicked.connect(lambda : self.close())
        self.main_vbox.addWidget(self.close_button)

    def add_func(self):
        self.viewer.startSelectMode()


    def add_crop(self, rect):
        height_coeff = self.image_height / IMAGE_HEIGHT
        width_coeff = self.image_width / IMAGE_WIDTH
        center_x =int( (rect.topLeft().x() + rect.bottomRight().x()) / 2 * width_coeff)
        center_y = int((rect.topLeft().y() + rect.bottomRight().y()) / 2 * height_coeff)
        rw = int(rect.width() * width_coeff / 2)
        rh = int(rect.height() * height_coeff / 2)
        self.crops.append({"center_x": center_x, "center_y": center_y, "rw": rw, "rh": rh})


    def update_count(self,):
        self.create_masked_image()
        counts = self.channels.count_blobs(self.SELECTED_COLORS, self.mask)
        text = "\n"
        for key, value in counts.items():
            text += key + ":    " + str(value) + "\n"
        self.label.setText(text)



    def undo_func(self):
        if len(self.crops) > 0 :
            self.crops.pop()
        self.viewer.pop_item()
        self.update_count()

    def mask_func(self):
        if self.mask_button.text() == "Mask":
            self.add_button.setEnabled(False)
            self.undo_button.setEnabled(False)
            self.mask_mode = True
            self.mask_button.setText("UnMask")
            self.create_masked_image()
            self.viewer.remove_all_items()
        else:
            self.add_button.setEnabled(True)
            self.undo_button.setEnabled(True)
            self.mask_mode = False
            self.mask_button.setText("Mask")
            self.viewer.add_all_items()
        self.show_image()


    def create_masked_image(self):
        if len(self.crops) == 0 :
            self.mask = np.ones_like(self.masked_image).astype(np.uint8)
            self.masked_image = (self.image * self.mask).astype(np.uint8)
            return
        self.mask = np.zeros_like(self.masked_image)
        angle = 0
        startAngle = 0
        endAngle = 360
        color = (1,1,1)
        thickness = -1
        for item in self.crops:
            self.mask = cv2.ellipse(self.mask, (item["center_x"], item["center_y"]),
                               (item["rw"], item["rh"]),
                               angle, startAngle, endAngle, color, thickness).astype(np.uint8)
            self.mask = np.where(self.mask > 0, 1, 0).astype(np.uint8)
        self.masked_image = (self.image * self.mask).astype(np.uint8)


    def show_image(self):

        image = self.image if not self.mask_mode else self.masked_image
        new_image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_WIDTH))
        height, width, channel = new_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(new_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)
        if not self.setup_bool:
            self.viewer.setPhoto(pixmap)
            self.setup_bool = True
        else:
            self.viewer.update_photo(pixmap)






