from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from ColorWindow import ColorWindow
from Adjustments import Adjustments
from PhotoViewer import PhotoViewer
from SelectionWindow import SelectionWindow
from CountWindow import CountWindow
from WholeCountWindow import  WholeCountWindow


class MyWindow(QWidget):
    def __init__(self, channels):
        super(MyWindow, self).__init__()
        self.channels = channels
        ## channel that we are moving using move button
        self.move_channel = None
        ## visible and selected colors by the user
        self.SELECTED_COLORS = set()
        ## there are two move modes "whole" and "part", in whole mode you can move the whole channel, in part mode just a selected part by user
        self.move_mode = "whole"
        ## all widths and heights of windows are in  constants file
        self.setGeometry(100, 100, MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)
        ## this window's size is not changeable
        self.setFixedHeight(MAINWINDOW_HEIGHT)
        self.setFixedWidth(MAINWINDOW_WIDTH)

        ## main layout of the my window class
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        ## to group buttons to active/deactive them when required
        self.buttonGroup = QButtonGroup()

        ## image vbox contains the image viewer and zoom in/out buttons, when viewer is in "whole" move mode a hbox containing two
        # buttons of Done and Reload is added to this vbox
        self.image_vbox = QVBoxLayout()
        self.main_layout.addLayout(self.image_vbox)
        self.viewer = PhotoViewer(self, IMAGE_WIDTH, IMAGE_HEIGHT, channels=self.channels)
        self.image_vbox.addWidget(self.viewer)
        self.viewer.setPhoto(QPixmap("template.jpg").scaled(IMAGE_WIDTH, IMAGE_HEIGHT))

        ## hbox for move buttons in "whole" mode
        self.move_hbox = QHBoxLayout()
        self.accept_move_button = QPushButton("Done ")
        self.accept_move_button.setIcon(QIcon("icons/check.png"))
        self.accept_move_button.setLayoutDirection(Qt.RightToLeft)
        self.accept_move_button.setStyleSheet("color:white; background-color: green; font-weight:bold; border:None")
        self.accept_move_button.clicked.connect(self.accept_move)
        self.accept_move_button.hide()
        self.accept_move_button.setFixedHeight(20)
        self.reload_button = QPushButton("Reload ")
        self.reload_button.setIcon(QIcon("icons/reload.png"))
        self.reload_button.setLayoutDirection(Qt.RightToLeft)
        self.reload_button.setStyleSheet("color:white; background-color: indianred; font-weight:bold; border:None")
        self.reload_button.clicked.connect(self.reset_move)
        self.reload_button.hide()
        self.reload_button.setFixedHeight(20)
        self.move_hbox.addWidget(self.reload_button)
        self.move_hbox.addWidget(self.accept_move_button)
        self.image_vbox.addLayout(self.move_hbox)

        ## add zoom in/out buttons
        self.create_zoom()

        ## main vbox contains channels with operation buttons for each and add channel button
        self.main_vbox = QVBoxLayout()
        label = QLabel("Channels")
        label.setFixedHeight(50)
        label.setFixedWidth(SCROLLAREA_WIDTH)
        label.setStyleSheet("background-color: gray; font-weight:bold; border-radius: 5px")
        label.setAlignment(Qt.AlignCenter)
        self.main_vbox.addWidget(label)

        ## scroll area for channels and their buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("border:None; background-color:gray; border-radius: 5px")
        self.scroll_widget = QWidget()
        self.scroll_vbox = QVBoxLayout()
        self.scroll_vbox.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setFixedWidth(SCROLLAREA_WIDTH)
        self.scroll_area.setFixedHeight(SCROLLAREA_HEIGHT)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_vbox.addWidget(self.scroll_area)

        self.create_add_button()
        self.create_count_button()
        self.create_invert_button()

        self.main_layout.addLayout(self.main_vbox)

        self.create_menus()

        self.show()

    def create_zoom(self):
        ## this function adds two buttons for zoom in and out
        self.zoom_hbox = QHBoxLayout()
        self.zoom_hbox.setAlignment(Qt.AlignCenter)
        self.image_vbox.addLayout(self.zoom_hbox)
        self.zoomin_button = QPushButton()
        self.zoomout_button = QPushButton()
        self.zoomin_button.setStyleSheet("border:None; background-image: url('icons/zoom-in(2).png');")
        self.zoomout_button.setStyleSheet("border:None; background-image: url('icons/zoom-out(2).png'); ")
        self.zoomin_button.setFixedWidth(20)
        self.zoomin_button.setFixedHeight(20)
        self.zoomout_button.setFixedHeight(20)
        self.zoomout_button.setFixedWidth(20)
        self.zoomin_button.clicked.connect(lambda: self.viewer.zoomIn())
        self.zoomout_button.clicked.connect(lambda: self.viewer.zoomOut())
        self.zoom_hbox.addWidget(self.zoomin_button)
        self.zoom_hbox.addWidget(self.zoomout_button)

    def create_menus(self):
        pass
        # ## this function creates menu for the main window
        # self.menubar = QMenuBar()
        # self.fileMenu = QMenu("File")
        # self.menubar.addMenu(self.fileMenu)
        # # self.fileMenu.addAction("Add channel", self.clicked_btn)
        #
        # self.invert_action = self.fileMenu.addAction("invert", self.invert)
        # self.uninvert_action = self.fileMenu.addAction("uninvert", self.uninvert)
        # self.invert_action.setEnabled(False)
        # self.uninvert_action.setEnabled(False)
        # self.main_layout.setMenuBar(self.menubar)

    def invert(self):
        ## after clicking on "invert" in file menu, this function is called, this function turns on the invert mode in Channels class
        self.channels.StartInvertMode()
        self.update_image()
        # self.uninvert_action.setEnabled(True)
        # self.invert_action.setEnabled(False)
        self.invert_btn.setText("UnInvert")

    def uninvert(self):
        ## this function turns off the invert mode in Channels class
        self.channels.EndInvertMode()
        self.update_image()
        # self.uninvert_action.setEnabled(False)
        # self.invert_action.setEnabled(True)
        self.invert_btn.setText("Invert")

    def create_add_button(self):
        ## this function adds "add channel" button
        btn1 = QPushButton("  Add channel!")
        btn1.setFixedWidth(SCROLLAREA_WIDTH)
        btn1.setFixedHeight(50)
        btn1.setFixedWidth(SCROLLAREA_WIDTH)
        btn1.setStyleSheet("background-color: #009688; color: white;  border-radius: 5px; font-weight: bold; border: 4px solid gray;")
        btn1.setIcon(QIcon("icons/plus.png"))
        btn1.clicked.connect(self.open_color_window)
        self.buttonGroup.addButton(btn1)
        self.main_vbox.addWidget(btn1)

    def create_count_button(self):
        ## this function adds "count" button
        self.count_btn = QPushButton("  Count")
        self.count_btn.setFixedWidth(SCROLLAREA_WIDTH)
        self.count_btn.setFixedHeight(50)
        self.count_btn.setFixedWidth(SCROLLAREA_WIDTH)
        self.count_btn.setStyleSheet("background-color: #3ebda8; color: white;  border-radius: 5px; font-weight: bold; border: 4px solid gray;")
        self.count_btn.setIcon(QIcon("icons/abacus.png"))
        self.count_btn.clicked.connect(self.open_whole_count)
        self.buttonGroup.addButton(self.count_btn )
        self.main_vbox.addWidget(self.count_btn )
        self.count_btn.setEnabled(False)

    def create_invert_button(self):
        ## this function adds "invert" button
        self.invert_btn = QPushButton("  Invert")
        self.invert_btn.setFixedWidth(SCROLLAREA_WIDTH)
        self.invert_btn.setFixedHeight(50)
        self.invert_btn.setFixedWidth(SCROLLAREA_WIDTH)
        self.invert_btn.setStyleSheet("background-color: #86d1c5; color: white;  border-radius: 5px; font-weight: bold; border: 4px solid gray;")
        self.invert_btn.clicked.connect(self.click_invert_btn)
        self.invert_btn.setIcon(QIcon("icons/exchange.png"))
        self.invert_btn.setEnabled(False)
        self.buttonGroup.addButton(self.invert_btn)
        self.main_vbox.addWidget(self.invert_btn)

    def click_invert_btn(self):
        if self.invert_btn.text() == "Invert":
            self.invert()
        else:
            self.uninvert()

    def update_channel_list(self, color):
        ## if the color was not added before, is added here
        if color not in self.SELECTED_COLORS:
            self.SELECTED_COLORS.add(color)
            if color == "Dapi":
                self.invert_btn.setEnabled(True)
                # self.invert_action.setEnabled(True)
                # self.uninvert_action.setEnabled(False)
            new_hbox = QHBoxLayout()
            ## visibility button for hide/show the channel
            visibility_btn = QToolButton()
            visibility_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            visibility_btn.setIcon(QIcon("icons/visibility.png"))
            visibility_btn.setStyleSheet("border:None")
            visibility_btn.clicked.connect(lambda: self.hide_and_show(color, visibility_btn))
            new_hbox.addWidget(visibility_btn)
            ## label for name of the channel
            name_label = QLabel(color)
            name_label.setStyleSheet("font-weight:bold;")
            new_hbox.addWidget(name_label)
            new_hbox.addStretch(8)
            ## add move feature for the channel
            move_button = QToolButton()
            move_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            move_button.setIcon(QIcon("icons/move.png"))
            move_button.setStyleSheet("border:None;")
            move_button.setToolTip("move")
            new_hbox.addWidget(move_button)
            move_button.clicked.connect(lambda: self.open_select_move(color))

            ## add adjustment feature for the channel
            adjust_button = QToolButton()
            adjust_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            adjust_button.setIcon(QIcon("icons/equalizer.png"))
            adjust_button.setStyleSheet("border:None;")
            adjust_button.setToolTip("adjust")
            adjust_button.clicked.connect(lambda: self.open_select_adjust(color))
            new_hbox.addWidget(adjust_button)

            ## add count feature for the channel
            count_button = QToolButton()
            count_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            count_button.setIcon(QIcon("icons/counter.png"))
            count_button.setStyleSheet("border:None;")
            count_button.setToolTip("count")
            count_button.clicked.connect(lambda: self.open_select_count(color))
            new_hbox.addWidget(count_button)

            ## add delete button for the channel
            delete_btn = QToolButton()
            delete_btn.setToolTip("delete")
            delete_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            delete_btn.setIcon(QIcon("icons/bin.png"))
            delete_btn.setStyleSheet("border:None")
            new_hbox.addWidget(delete_btn)

            self.scroll_vbox.addLayout(new_hbox)

            ## after each channel features, we add a line separator
            Separator = QFrame(self)
            Separator.setFrameShape(QFrame.HLine)
            Separator.setFrameShadow(QFrame.Sunken)
            Separator.setStyleSheet("background-color:black;")
            Separator.setLineWidth(1)
            self.scroll_vbox.addWidget(Separator)

            ## all buttons of the channel are added to a unique group for turning them on/off in special occasions such as move
            self.buttonGroup.addButton(adjust_button)
            self.buttonGroup.addButton(move_button)
            self.buttonGroup.addButton(delete_btn)



            delete_btn.clicked.connect(lambda: self.make_sure_delete(new_hbox, Separator, color))

        self.update_image()

    def make_sure_delete(self, new_hbox, Separator, color):
        ## this function shows a message box to make sure you want to delete a channel
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Are you sure you want to delete this channel?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == QMessageBox.Ok:
            self.delete_channel(new_hbox, Separator, color)

    def move_whole_func(self, color):
        ## this function is called when a user chooses "whole image" for moving
        self.move_channel = color
        self.move_mode = "whole"
        self.viewer.startWholeMoveMode(color)
        ## two accept and reload buttons are shown
        self.accept_move_button.show()
        self.reload_button.show()
        for button in self.buttonGroup.buttons():
            button.setEnabled(False)

    def move_part_func(self):
        self.accept_move_button.show()
        self.reload_button.show()

    def accept_move(self):
        if self.move_mode == "whole":
            self.viewer.EndWholeMoveMode()
        else:
            ## accept changes on part of the image
            self.channels.accept_move_change(self.move_channel)
        self.move_channel = None
        ## activate buttons after accepting the move
        for button in self.buttonGroup.buttons():
            button.setEnabled(True)
        self.accept_move_button.hide()
        self.reload_button.hide()

    def reset_move(self):
        if self.move_mode == "whole":
            ## this will delete the shifts
            self.channels.reset_shift(self.move_channel)
        else:
            self.channels.reset_move_change(self.move_channel)
            self.accept_move_button.hide()
            self.reload_button.hide()
            for button in self.buttonGroup.buttons():
                button.setEnabled(True)
        self.update_image()

    def open_select_adjust(self, color):
        ## opens a window asking if a user want to adjust the whole channel or part of it
        selection_window = SelectionWindow(self, color,
                                           "For adjustment you have to specify the fragment you want to edit.",
                                           for_adjust=True)
        selection_window.setWindowModality(Qt.ApplicationModal)
        selection_window.show()

    def open_select_move(self, color):
        ## opens a window asking if a user want to move the whole channel or part of it
        selection_window = SelectionWindow(self, color,
                                           "For movement you have to specify the fragment you want to move.",
                                           for_move=True)
        selection_window.setWindowModality(Qt.ApplicationModal)
        selection_window.show()

    def open_select_count(self, color):
        ## opens a window asking if a user want to count signals of the whole channel or part of it
        selection_window = SelectionWindow(self, color,
                                           "For counting you have to specify the fragment you want to see.",
                                           for_count=True)
        selection_window.setWindowModality(Qt.ApplicationModal)
        selection_window.show()

    def delete_channel(self, hbox, line, color):
        ## delete all items in the hbox of the chosen channel and the corresponding separator
        for i in reversed(range(hbox.count())):
            item = hbox.itemAt(i)

            if isinstance(item, QWidgetItem):
                item.widget().close()
        line.deleteLater()

        self.SELECTED_COLORS.remove(color)
        if color == "Dapi":
            self.invert_btn.setEnabled(False)
            self.invert_btn.setText("Invert")
            self.channels.EndInvertMode()
            # self.invert_action.setEnabled(False)
            # self.uninvert_action.setEnabled(False)
        self.channels.delete_channel(color)
        self.update_image()

    def open_adjust(self, color, begin_x, begin_y, width, height):
        ## get the selected image and pass it to the adjust window
        image = self.channels.get_image(color)[begin_y:begin_y + height, begin_x:begin_x + width]
        self.adjust_window = Adjustments(self, image, begin_x, begin_y, color, self.channels)
        self.adjust_window.setWindowModality(Qt.ApplicationModal)
        self.adjust_window.show()

    def open_whole_count(self):
        image = self.channels.sum_channels(self.SELECTED_COLORS)[0:IMAGE_HEIGHT, 0:IMAGE_HEIGHT]
        self.w_count_window = WholeCountWindow(self, self.channels, image, self.SELECTED_COLORS)
        self.w_count_window.setWindowModality(Qt.ApplicationModal)
        self.w_count_window.show()

    def open_count(self, color, begin_x, begin_y, width, height):
        ## get the selected image and pass it to the count window
        image = self.channels.get_image(color)[begin_y:begin_y + height, begin_x:begin_x + width]
        self.count_window = CountWindow(self, self.channels, image, color, begin_x, begin_y)
        self.count_window.setWindowModality(Qt.ApplicationModal)
        self.count_window.show()

    def select_for_count(self, color):
        ## after clicking "part of image" for count item
        self.viewer.startSelectCountMode(color)

    def select_for_adjust(self, color):
        ## after clicking "part of image" in ajust item
        self.viewer.startSelectAdjustMode(color)

    def select_for_move(self, color):
        ## after clicking "part of image" in move item
        self.move_mode = "part"
        self.move_channel = color
        for button in self.buttonGroup.buttons():
            button.setEnabled(False)
        self.viewer.startSelectMoveMode(color)

    def hide_and_show(self, color, btn):
        ## after clicking the visibility button of a chosen channel, this function is called
        if color in self.SELECTED_COLORS:
            btn.setIcon(QIcon("icons/hide.png"))
            self.SELECTED_COLORS.remove(color)
        else:
            btn.setIcon(QIcon("icons/visibility.png"))
            self.SELECTED_COLORS.add(color)
        self.update_image()

    def update_image(self):
        ## this function is needed to be called for reloading changes on image
        img = self.channels.sum_channels(self.SELECTED_COLORS)
        if img.size == 0:
            self.viewer.update_photo(QPixmap())
            self.count_btn.setEnabled(False)
        else:
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qImg = QImage(img.data.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap(qImg)
            self.viewer.update_photo(pixmap)
            self.count_btn.setEnabled(True)

    def open_color_window(self):
        ## after clicking on "add" button, a dialog will open and after that a window for choosing the color
        image = QFileDialog.getOpenFileName(None, 'OpenFile', '', "*.jpg *.png *.tif *.tiff *.bmp *.JPG")
        imagePath = image[0]
        if imagePath != "":
            self.color_window = ColorWindow(imagePath, self, self.channels)
            self.color_window.setWindowModality(Qt.ApplicationModal)
            self.color_window.show()
