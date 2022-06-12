from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from Position import Position
import cv2


class CountViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent, WIDTH, HEIGHT, channels=None, color=None):
        super(CountViewer, self).__init__(parent)
        self._zoom = 0
        self.image_width = WIDTH
        self.image_height = HEIGHT
        self.parent = parent
        self._empty = True
        self.items = []
        self.channels = channels
        self.color = color
        self.select_mode = False
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
        self.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.setFrameShape(QFrame.NoFrame)
        self.begin, self.destination = QPoint(), QPoint()

    def drawEllipse(self, coords1, coords2):
        ## change the rect item according to two input coordinates
        r = QRectF(coords1, coords2)

        self._current_ellipse_item.setRect(r.normalized())


    def add_ellipse(self):
        self._current_ellipse_item = QGraphicsEllipseItem()
        self._current_ellipse_item.setPen(Qt.red)
        self._scene.addItem(self._current_ellipse_item)
        self.items.append(self._current_ellipse_item)

    def remove_all_items(self):
        for item in self.items:
            self._scene.removeItem(item)

    def add_all_items(self):
        for item in self.items:
            self._scene.addItem(item)

    def pop_item(self):
        if len(self.items) > 0:
            item = self.items.pop()
            self._scene.removeItem(item)

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
        ## for zoomi in/out
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


    def startSelectMode(self):
        self.toggleDragMode()
        self.select_mode = True

    def endSelectMode(self):
        self.select_mode = False

    def mousePressEvent(self, event):
        if self.select_mode:
            if event.buttons() & Qt.LeftButton:
                self.begin = self.mapToScene(event.pos()).toPoint()
                self.destination = self.begin
                self.add_ellipse()



        super(CountViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.select_mode:
            if event.buttons() & Qt.LeftButton:
                ## just draw rectangle with the coordinates of the press event and current coordinates
                self.destination = self.mapToScene(event.pos()).toPoint()
                self.drawEllipse(self.begin, self.destination)


        super(CountViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.select_mode:
            ## after selecting open adjust window in the previous class
            if event.button() & Qt.LeftButton:
                self.drawEllipse(self.begin, self.destination)
                rect = QRectF(self.begin, self.destination).normalized()
                self.parent.add_crop(rect)
                self.parent.update_count()

            self.toggleDragMode()
            self.endSelectMode()



        super(CountViewer, self).mouseReleaseEvent(event)
