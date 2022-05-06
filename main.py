import sys
from PyQt5.QtWidgets import *
from MyWindow import MyWindow
from Channels import Channels
## main application
app = QApplication(sys.argv)
## all processing on images and channels are done in Channels class and its functions
channels = Channels()
##first and main window
window = MyWindow(channels)
sys.exit(app.exec_())
