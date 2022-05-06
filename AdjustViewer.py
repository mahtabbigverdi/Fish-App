from PyQt5.QtWidgets import  *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
import numpy as np
import cv2

class AdjustViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent,  WIDTH, HEIGHT, channels=None, color=None):
        super(AdjustViewer, self).__init__(parent)
        self._zoom = 0
        self.image_width = WIDTH
        self.image_height = HEIGHT
        self.crop_mode = False
        self.parent = parent
        self._empty = True
        self.delete_mode = False
        self.channels = channels
        self.color = color
        self._scene = QGraphicsScene(self)
        self.setGeometry(200, 200, self.image_width, self.image_height)
        self.setFixedHeight(self.image_height)
        self.setFixedWidth(self.image_width)
        self.viewport().setFixedHeight(self.image_height)
        self.viewport().setFixedWidth(self.image_width)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

        self._current_rect_item = QGraphicsRectItem()
        # self._current_rect_item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self._current_rect_item.setPen(Qt.white)
        self._scene.addItem(self._current_rect_item)

        self._current_ellipse_item = QGraphicsEllipseItem()
        self._current_ellipse_item.setPen(Qt.white)
        self._scene.addItem(self._current_ellipse_item)

        self.begin, self.destination = QPoint(), QPoint()



    def drawEllipse(self, coords1, coords2):
        self._current_ellipse_item.setRect(QRectF(coords1, coords2).normalized())


    def drawRect(self, coords1, coords2):
        r = QRectF(coords1, coords2)
        self._current_rect_item.setRect(r.normalized())

    def hasPhoto(self):
        return not self._empty


    def update_photo(self, pixmap):
        self._photo.setPixmap(pixmap)


    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
                # print(factor, viewrect.width() , scenerect.width(),viewrect.height() , scenerect.height())
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())

        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0


    def zoomIn(self):
        if self.hasPhoto():
            factor = 1.25
            self._zoom += 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def zoomOut(self):
        if self.hasPhoto():
            factor = 0.8
            self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def startDeleteMode(self):
        self.delete_mode = True
        self.setDragMode(QGraphicsView.NoDrag)

    def endDeleteMode(self):
        self.delete_mode = False
        self.toggleDragMode()

    def startCropMode(self):
        self.crop_mode = True
        self.setDragMode(QGraphicsView.NoDrag)

    def endCropMode(self):
        self.crop_mode = False
        self.toggleDragMode()

    def mousePressEvent(self, event):
        if self.delete_mode or self.crop_mode:
            if event.buttons() & Qt.LeftButton:
                self.begin =  self.mapToScene(event.pos()).toPoint()
                self.destination = self.begin
        super(AdjustViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.delete_mode :
            if event.buttons() & Qt.LeftButton:
                self.destination =  self.mapToScene(event.pos()).toPoint()
                self.drawRect(self.begin, self.destination)
        elif self.crop_mode :
            if event.buttons() & Qt.LeftButton:
                self.destination =  self.mapToScene(event.pos()).toPoint()
                self.drawEllipse(self.begin, self.destination)

        super(AdjustViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.delete_mode:
            if event.button() & Qt.LeftButton:
                self.drawRect(self.begin, self.destination)
                self.parent.add_deletion(self.begin , self.destination)
                self.parent.show_image()
            self.begin, self.destination = QPoint(), QPoint()
            self.drawRect(self.begin, self.destination)
            self.endDeleteMode()
        elif self.crop_mode:
            if event.button() & Qt.LeftButton:
                self.drawEllipse(self.begin, self.destination)
                self.parent.add_crop(QRectF(self.begin, self.destination).normalized())
                self.parent.show_image()
            self.begin, self.destination = QPoint(), QPoint()
            self.drawEllipse(self.begin, self.destination)
            self.endCropMode()



        super(AdjustViewer, self).mouseReleaseEvent(event)



