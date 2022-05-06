from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from Position import Position
import cv2


class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent, WIDTH, HEIGHT, channels=None, color=None):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self.image_width = WIDTH
        self.image_height = HEIGHT
        self.parent = parent
        self._empty = True
        self.select_for_adjust_mode = False
        self.select_for_count_mode = False
        self.whole_move_mode = False
        self.part_move_mode = False
        self.counter_mode = False
        self.start_move_pos = None
        self.channels = channels
        self.color = color
        self.move_channel = None
        self.select_for_move_mode = False
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

        self._current_rect_item = QGraphicsRectItem()
        # self._current_rect_item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self._current_rect_item.setPen(Qt.white)
        self._scene.addItem(self._current_rect_item)
        self.begin, self.destination = QPoint(), QPoint()

    def drawRect(self, coords1, coords2):

        r = QRectF(coords1, coords2)

        self._current_rect_item.setRect(r.normalized())

    def setCursorPositionInRect(self, rect, destination):
        if rect.bottomLeft() == destination:
            return Position.BottomLeft
        elif rect.bottomRight() == destination:
            return Position.BottomRight
        elif rect.topLeft() == destination:
            return Position.TopLeft
        else:
            return Position.TopRight

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

    def startWholeMoveMode(self, color):
        self.whole_move_mode = True
        self.move_channel = color

    def EndWholeMoveMode(self):
        self.whole_move_mode = False
        self.move_channel = None

    def startPartMoveMode(self, destination, rect):
        self.cursorPosRect = self.setCursorPositionInRect(rect, self.destination)
        self.part_move_mode = True
        self.start_move_pos = destination
        self.moved_part = self.channels.get_image(self.move_channel)[int(rect.y()):int(rect.y() + rect.height()),
                          int(rect.x()):int(rect.x() + rect.width())].copy()

        topleft = self.getTopLeft(self.start_move_pos)
        self.channels.add_move_delete(self.move_channel, int(topleft.x()), int(topleft.y()), self.moved_part.shape[1], self.moved_part.shape[0])

    def EndPartMoveMode(self):
        self.part_move_mode = False
        self.move_channel = None
        self.cursorPosRect = None
        self.moved_part = None
        self.start_move_pos = None
        self.drawRect(QPointF(), QPointF())

    def getTopLeft(self, destination):
        if self.cursorPosRect == Position.TopLeft:
            return self.cursorPosRect
        elif self.cursorPosRect == Position.BottomLeft:
            return QPointF(destination.x(), destination.y() - self.moved_part.shape[0] )
        elif self.cursorPosRect == Position.BottomRight:
            return QPointF(destination.x() - self.moved_part.shape[1], destination.y() - self.moved_part.shape[0] )
        else:
            return QPointF(destination.x() - self.moved_part.shape[1], destination.y())

    def startSelectAdjustMode(self, color):
        self.color = color
        self.select_for_adjust_mode = True
        self.setDragMode(QGraphicsView.NoDrag)

    def startSelectCountMode(self, color):
        self.color = color
        self.select_for_count_mode = True
        self.setDragMode(QGraphicsView.NoDrag)

    def startSelectMoveMode(self, color):
        self.move_channel = color
        self.select_for_move_mode = True
        self.setDragMode(QGraphicsView.NoDrag)

    def mousePressEvent(self, event):
        if self.select_for_adjust_mode or self.whole_move_mode or self.select_for_move_mode or self.part_move_mode or self.select_for_count_mode:
            if event.buttons() & Qt.LeftButton:
                self.begin = self.mapToScene(event.pos()).toPoint()
                self.destination = self.begin
        if self.counter_mode:
            if event.buttons() & Qt.LeftButton:
                self.begin = self.mapToScene(event.pos()).toPoint()
                self.parent.check_point(self.begin)


        super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.select_for_adjust_mode or self.select_for_move_mode or self.select_for_count_mode:
            if event.buttons() & Qt.LeftButton:
                self.destination = self.mapToScene(event.pos()).toPoint()
                self.drawRect(self.begin, self.destination)
        elif self.whole_move_mode:
            if event.buttons() & Qt.LeftButton:
                self.destination = self.mapToScene(event.pos()).toPoint()
                HShift = self.destination.x() - self.begin.x()
                VShift = self.destination.y() - self.begin.y()
                self.channels.apply_shift(self.move_channel, HShift, VShift)
                self.parent.update_image()
                self.begin = self.destination
        elif self.part_move_mode:
            if event.buttons() & Qt.LeftButton:
                self.destination = self.mapToScene(event.pos()).toPoint()
                topleft = self.getTopLeft(self.destination)
                new_rect = QRectF(topleft, QSizeF(self.moved_part.shape[1], self.moved_part.shape[0]))
                self._current_rect_item.setRect(new_rect)
                self.channels.add_move_change(self.move_channel, self.moved_part, int(topleft.x()), int(topleft.y()), self.moved_part.shape[1], self.moved_part.shape[0])
                self.parent.update_image()
        super(PhotoViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.select_for_adjust_mode:
            if event.button() & Qt.LeftButton:
                self.drawRect(self.begin, self.destination)
                rect = QRectF(self.begin, self.destination).normalized()
                self.parent.open_adjust(self.color, int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))
            self.begin, self.destination = QPoint(), QPoint()
            self.drawRect(self.begin, self.destination)
            self.toggleDragMode()
            self.select_for_adjust_mode = False
        elif self.select_for_move_mode:
            if event.button() & Qt.LeftButton:
                self.toggleDragMode()
                self.select_for_move_mode = False
                self.drawRect(self.begin, self.destination)
                rect = QRectF(self.begin, self.destination).normalized()

                self.startPartMoveMode(self.destination, rect)

        elif self.select_for_count_mode:
            if event.button() & Qt.LeftButton:
                self.drawRect(self.begin, self.destination)
                rect = QRectF(self.begin, self.destination).normalized()
                self.parent.open_count(self.color, int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))
            self.begin, self.destination = QPoint(), QPoint()
            self.drawRect(self.begin, self.destination)
            self.toggleDragMode()
            self.select_for_count_mode = False
        elif self.part_move_mode:
            self.EndPartMoveMode()
            self.parent.move_part_func()

        super(PhotoViewer, self).mouseReleaseEvent(event)
