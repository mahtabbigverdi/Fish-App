import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Constants import *
from Channels import Channels
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import cv2
from PhotoViewer import PhotoViewer

class Adjustments(QWidget):
    def __init__(self, color, main_window, channels):
        super().__init__()
        self.change_occured = False
        self.setup_bool = False
        self.main_window = main_window
        self.color = color
        self.channels = channels
        self.temp_alpha = self.channels.alphas[self.color]
        self.temp_beta = self.channels.betas[self.color]
        self.temp_thresh = self.channels.thresholds[self.color]
        self.temp_noise = self.channels.noises[self.color]
        self.setFixedHeight(ADJUSTWINDOW_HEIGHT)
        self.setFixedWidth(ADJUSTWINDOW_WIDTH)
        ## MAIN LAYOUT
        self.main_layout = QVBoxLayout()
        self.layout = QHBoxLayout()
        self.main_layout.addLayout(self.layout)
        self.create_image_label()
        self.adjust_vbox = QVBoxLayout()
        self.create_contrast()
        self.create_brightness()
        self.create_threshold()
        self.create_noise()
        self.create_delete()
        self.layout.addLayout(self.adjust_vbox)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        self.apply_button.clicked.connect(lambda: self.apply_click())
        self.main_layout.addWidget(self.apply_button)
        self.setLayout(self.main_layout)


    def apply_click(self):
        self.change_occured = True
        self.channels.alphas[self.color] = self.temp_alpha
        self.channels.betas[self.color] = self.temp_beta
        self.channels.thresholds[self.color] = self.temp_thresh
        self.channels.noises[self.color] = self.temp_noise
        self.main_window.update_image()
        self.close()



    def create_delete(self):
        self.delete_hbox = QHBoxLayout()
        self.adjust_vbox.addLayout(self.delete_hbox)
        self.delete_btn = QPushButton("delete")
        self.delete_hbox.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.delete_func)
        self.delete_btn.setFixedHeight(30)
        self.delete_btn.setStyleSheet("border-radius: 3px; background-color:#80100a; color:white")
        self.undo_btn = QPushButton("undo")
        self.delete_hbox.addWidget(self.undo_btn)
        self.undo_btn.clicked.connect(self.undo_func)
        self.undo_btn.setStyleSheet("border-radius: 3px; background-color:#1c81b8; color:black")
        self.undo_btn.setFixedHeight(30)



    def undo_func(self):
        out  = self.channels.undo_deletion(self.color)
        if out:
            self.show_image()
        else:
            self.make_error("No more deletions to undo")

    def delete_func(self):
        self.viewer.startDeleteMode()

    def create_noise(self):
        self.noise_hbox = QHBoxLayout()
        self.adjust_vbox.addLayout(self.noise_hbox)
        label = QLabel("Denoise")
        self.noise_hbox.addWidget(label)
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_hbox.addWidget(self.noise_slider)
        self.noise_slider.setMinimum(0)
        self.noise_slider.setMaximum(10)
        # print("noise", self.temp_noise)
        self.noise_slider.setValue(self.temp_noise)
        self.noise_slider.valueChanged.connect(lambda: self.update_noise(self.noise_slider.value()))
        self.noise_input = QLineEdit()
        self.noise_hbox.addWidget(self.noise_input)
        self.noise_input.setText(str(self.temp_noise))
        self.noise_input.setFixedWidth(40)
        self.noise_input.setAlignment(Qt.AlignCenter)
        self.noise_input.returnPressed.connect(lambda: self.update_noise(self.noise_input.text()))

    def create_threshold(self):
        self.threshold_hbox = QHBoxLayout()
        self.adjust_vbox.addLayout(self.threshold_hbox)
        label = QLabel("Threshold")
        self.threshold_hbox.addWidget(label)
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_hbox.addWidget(self.threshold_slider)
        self.threshold_slider.setMinimum(int(self.channels.initial_thresh[self.color]))
        self.threshold_slider.setMaximum(255)
        # print("threshold", self.temp_thresh)
        self.threshold_slider.setValue(self.temp_thresh)
        self.threshold_slider.valueChanged.connect(lambda: self.update_threshold(self.threshold_slider.value()))
        self.threshold_input = QLineEdit()
        self.threshold_hbox.addWidget(self.threshold_input)
        self.threshold_input.setText(str(self.temp_thresh))
        self.threshold_input.setFixedWidth(40)
        self.threshold_input.setAlignment(Qt.AlignCenter)
        self.threshold_input.returnPressed.connect(lambda: self.update_threshold(self.threshold_input.text()))

    def create_contrast(self):
        self.contrast_hbox = QHBoxLayout()
        self.adjust_vbox.addLayout(self.contrast_hbox)
        label = QLabel("Contrast")
        self.contrast_hbox.addWidget(label)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_hbox.addWidget(self.contrast_slider)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(30)
        # print("alpha", self.temp_alpha)
        self.contrast_slider.setValue(self.temp_alpha)
        self.contrast_slider.valueChanged.connect(lambda: self.update_contrast(self.contrast_slider.value()))
        self.contrast_input = QLineEdit()
        self.contrast_hbox.addWidget(self.contrast_input)
        self.contrast_input.setText(str(self.temp_alpha))
        self.contrast_input.setFixedWidth(40)
        self.contrast_input.setAlignment(Qt.AlignCenter)
        self.contrast_input.returnPressed.connect(lambda: self.update_contrast(self.contrast_input.text()))

    def create_brightness(self):
        self.brightness_hbox = QHBoxLayout()
        self.adjust_vbox.addLayout(self.brightness_hbox)
        label = QLabel("Brightness")
        self.brightness_hbox.addWidget(label)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_hbox.addWidget(self.brightness_slider)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(self.temp_beta)
        self.brightness_slider.valueChanged.connect(lambda: self.update_brightness(self.brightness_slider.value()))
        self.brightness_input = QLineEdit()
        self.brightness_hbox.addWidget(self.brightness_input)
        self.brightness_input.setText(str(self.temp_beta))
        self.brightness_input.setFixedWidth(40)
        self.brightness_input.setAlignment(Qt.AlignCenter)
        self.brightness_input.returnPressed.connect(lambda: self.update_brightness(self.brightness_input.text()))

    def make_error(self, messgae):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(messgae)
        msg.setWindowTitle("Error")
        msg.exec_()

    def show_image(self):
        new_image = self.channels.dictionary[self.color].copy()
        new_image = self.channels.apply_deletions(self.color, new_image)
        if self.temp_thresh != self.channels.initial_thresh[self.color]:
            _, mask = cv2.threshold(cv2.cvtColor(new_image, cv2.COLOR_RGB2GRAY), self.temp_thresh,
                                    255, cv2.THRESH_BINARY)
            new_image = new_image * mask[..., None]
        new_image = cv2.addWeighted(new_image, self.temp_alpha,
                                    np.zeros(self.channels.dictionary[self.color].shape,
                                             self.channels.dictionary[self.color].dtype), 0,
                                    self.temp_beta)
        ##TODO
        new_image = np.where(new_image <= self.temp_beta, 0, new_image)
        new_image = self.denoise(new_image, self.temp_noise)
        height, width, channel = new_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(new_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)
        if self.setup_bool:
            self.viewer.update_photo(pixmap)
        else:
            self.viewer.setPhoto(pixmap)
            self.setup_bool = True
    def update_image(self, change):
        type = change[0]
        val = change[1]
        if type == "contrast":
            self.temp_alpha = val
            self.show_image()
        elif type == "brightness":
            self.temp_beta = val
            self.show_image()
        elif type == "Threshold":
            self.temp_thresh = val
            self.show_image()
        elif type == "Noise":
            self.temp_noise = val
            self.show_image()

    def update_noise(self, val):
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                self.make_error('Enter a integer between 0 and 10')
                return
            if val > 10 or val < 0:
                self.make_error('Enter a integer between 0 and 10')
                return

        self.noise_input.setText(str(val))
        self.noise_slider.setValue(int(val))
        self.update_image(("Noise", int(val)))

    def update_threshold(self, val):
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                self.make_error('Enter a integer between initial value and 255')
                return
            if val > 255 or val < self.channels.initial_thresh[self.color]:
                self.make_error('Enter a integer between initial value and 255')
                return

        self.threshold_input.setText(str(val))
        self.threshold_slider.setValue(int(val))
        self.update_image(("Threshold", int(val)))

    def update_contrast(self, val):
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                self.make_error('Enter a number between 0 and 3')
                return
            if val > 3 or val < 0:
                self.make_error('Enter a number between 0 and 3')
                return
            val = np.round(val, 1) * 10

        alpha = val / 10.0
        self.contrast_input.setText(str(alpha))
        self.contrast_slider.setValue(int(val))
        self.update_image(("contrast", alpha))

    def update_brightness(self, val):
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                self.make_error('Enter a number between 0 and 100')
                return
            if val > 100 or val < 0:
                self.make_error('Enter a number between 0 and 100')
                return

        self.brightness_input.setText(str(val))
        self.brightness_slider.setValue(int(val))
        self.update_image(("brightness", int(val)))

    def create_image_label(self):
        self.image_vbox = QVBoxLayout()
        self.layout.addLayout(self.image_vbox)
        self.viewer = PhotoViewer(self, self.channels, self.color)
        self.viewer.setPhoto(None)
        self.image_vbox.addWidget(self.viewer)
        self.show_image()
        self.create_zoom()

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

    def denoise(self, image, noise_value):
        im = image.copy()
        for i in range(noise_value):
            im = cv2.bilateralFilter(im, 5, 75, 75)
        return im

