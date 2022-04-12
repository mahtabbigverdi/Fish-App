from PyQt5.QtWidgets import  *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *

class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent, channels=None, color=None):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self.parent = parent
        self._empty = True
        self.delete_mode = False
        self.channels = channels
        self.color = color
        self._scene = QGraphicsScene(self)
        self.setGeometry(200, 200, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.setFixedHeight(IMAGE_HEIGHT)
        self.setFixedWidth(IMAGE_WIDTH)
        self.viewport().setFixedHeight(IMAGE_HEIGHT)
        self.viewport().setFixedWidth(IMAGE_WIDTH)
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
        self._current_rect_item.setPen(Qt.red)
        self._scene.addItem(self._current_rect_item)
        self.begin, self.destination = QPoint(), QPoint()



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

    # def mousePressEvent(self, event):
    #     if self._photo.isUnderMouse():
    #         self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
    #     super(PhotoViewer, self).mousePressEvent(event)



    def mousePressEvent(self, event):
        if self.delete_mode:
            if event.buttons() & Qt.LeftButton:
                self.begin =  self.mapToScene(event.pos()).toPoint()
                self.destination = self.begin
                # print(self.begin, self.destination, self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.delete_mode:
            if event.buttons() & Qt.LeftButton:
                self.destination =  self.mapToScene(event.pos()).toPoint()
                self.drawRect(self.begin, self.destination)
        super(PhotoViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.delete_mode:
            if event.button() & Qt.LeftButton:
                self.drawRect(self.begin, self.destination)
                self.channels.add_deletion(self.color, self.begin, self.destination)
                self.parent.show_image()
            self.begin, self.destination = QPoint(), QPoint()
            self.drawRect(self.begin, self.destination)

            self.toggleDragMode()
            self.delete_mode = False
        super(PhotoViewer, self).mouseReleaseEvent(event)



