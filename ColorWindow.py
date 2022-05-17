
from PyQt5.QtWidgets import *
from Constants import *


class ColorWindow(QWidget):
    def __init__(self,imagePath, main_window, channels):
        super().__init__()
        self.channels = channels
        self.main_window = main_window
        self.imagePath = imagePath
        self.setFixedHeight(COLORWINDOW_HEIGHT)
        self.setFixedWidth(COLORWINDOW_WIDTH)
        ## MAIN LAYOUT
        self.color_list = ["Dapi", "Red", "Green", "Gold", "Orange", "other"]
        layout = QVBoxLayout()

        ### CHOOSE COLOR FROM COMBO BOX
        self.choose_hbox = QHBoxLayout()
        self.question_label = QLabel("Choose the color of channel: ")
        self.choose_hbox.addWidget(self.question_label)
        ## choose color from combo box
        self.defined_colors = QComboBox()
        self.defined_colors.addItems(self.color_list)
        self.defined_colors.currentIndexChanged.connect(self.selectionchange)
        self.choose_hbox.addWidget(self.defined_colors)
        layout.addLayout(self.choose_hbox)

        ### Enter your own color
        self.new_color_hbox = QHBoxLayout()
        self.label = QLabel("Enter the color:")
        self.new_color_hbox.addWidget(self.label)
        self.label.hide()
        self.input_color = QLineEdit()
        self.input_color.setPlaceholderText(" write your color here...")
        self.input_color.setStyleSheet("border-radius: 2px")
        self.new_color_hbox.addWidget(self.input_color)
        self.input_color.hide()
        layout.addLayout(self.new_color_hbox)

        # Buttons
        self.buttons_hbox = QHBoxLayout()
        self.cancel_button = QPushButton("cancel")
        self.buttons_hbox.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.close_window)
        self.cancel_button.setStyleSheet("border-radius: 3px; background-color:black; color:white; border: 3px solid #607D8B ;")
        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedHeight(30)
        self.ok_button.setAutoDefault(True)
        self.cancel_button.setFixedHeight(30)
        self.ok_button.setStyleSheet("border-radius: 3px; background-color:black; color:white; border: 3px solid #009688;")

        self.ok_button.clicked.connect(self.insert_channel)
        self.buttons_hbox.addWidget(self.ok_button)
        layout.addLayout(self.buttons_hbox)

        self.setLayout(layout)


    def insert_channel(self):
        ## after clicking "OK", the image with chosen color will be inserted in the list in the Channels Class
        if self.defined_colors.currentText() != "other":
            self.channels.add_channel(self.defined_colors.currentText(),self.imagePath )
            self.main_window.update_channel_list(self.defined_colors.currentText())
            self.close()
        elif self.defined_colors.currentText() == "other" and self.input_color.text()!= "":
            self.channels.add_channel(self.input_color.text(), self.imagePath)
            self.main_window.update_channel_list(self.input_color.text())
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Enter the channel name')
            msg.setWindowTitle("Error")
            msg.exec_()

    def close_window(self):

        self.close()

    def selectionchange(self):
        ## if the user selects other, the editbox shows up
        if self.defined_colors.currentText() == "other":
            self.label.show()
            self.input_color.show()
        else:
            self.label.hide()
            self.input_color.hide()

