import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Constants import *
from PhotoViewer import PhotoViewer
import numpy as np
import cv2
class CountWindow(QWidget):
    def __init__(self, main_window, channels, image, color, begin_x, begin_y ):
        super().__init__()
        self.main_window = main_window
        self.color = color
        self.image = image
        self.image_height = self.image.shape[0]
        self.image_width = self.image.shape[1]
        self.channels = channels
        self.begin_x = begin_x
        self.begin_y = begin_y
        self.setup_bool = False
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        ## detector for detecting signals or blobs in a channel
        self.detector = cv2.SimpleBlobDetector_create()
        ## set parameters of the detecor
        self.set_detector()
        self.removeds = []
        self.setFixedWidth(COUNTWINDOW_WIDTH)
        self.setFixedHeight(COUNTWINDOW_HEIGHT)
        self.delete_label = QLabel("For deletion you can click on them")
        self.delete_label.setAlignment(Qt.AlignCenter)
        self.delete_label.setStyleSheet("background-color:black; color:white; font-weight: bold")
        self.main_layout.addWidget(self.delete_label)
        ## the viewer for image in count window
        self.viewer = PhotoViewer(self, COUNTIMAGE_WIDTH, COUNTIMAGE_HEIGHT)
        self.viewer.setPhoto(None)
        self.viewer.counter_mode = True
        self.main_layout.addWidget(self.viewer)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel()
        self.label.setFixedWidth(COUNTIMAGE_WIDTH)
        self.label.setFixedHeight(40)
        self.label.setStyleSheet("background-color: black; font-weight:bold; color: #009688")
        self.label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label)
        self.btn_hbox = QHBoxLayout()
        self.main_layout.addLayout(self.btn_hbox)
        self.apply_btn = QPushButton("apply")
        self.undo_btn = QPushButton("undo")
        self.undo_btn.setEnabled(False)
        self.apply_btn.setStyleSheet(
            "border-radius: 3px; background-color:black; color:white; border: 3px solid #009688;")
        self.undo_btn.setStyleSheet(
            "border-radius: 3px; background-color:black; color:white; border: 3px solid #e31773;")
        self.btn_hbox.addWidget(self.undo_btn)
        self.btn_hbox.addWidget(self.apply_btn)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.undo_btn.clicked.connect(self.undo_deletion)
        ## find contours and blobs
        self.process_image()
        ## draw contours and their numbers
        self.show_image()






    def show_image(self):
        ## draw all keypoints in teh list with a corresponding number
        new_image =  cv2.drawKeypoints(self.image, tuple(self.keypoints), np.array([]), (255, 255, 255),
                                 cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        for i in range(len(self.keypoints)):
            keypoint = self.keypoints[i]
            x = int(keypoint.pt[0] + keypoint.size // 2 + 2)
            y = int(keypoint.pt[1])
            cv2.putText(new_image, str(i+1), (x,y), cv2.FONT_HERSHEY_DUPLEX, 1, (127,255,127), 1, cv2.LINE_AA )

        new_image = cv2.resize(new_image, (COUNTIMAGE_WIDTH, COUNTIMAGE_HEIGHT))
        height, width, channel = new_image.shape
        bytesPerLine = 3 * width
        qImg = QImage(new_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)
        if not self.setup_bool:
            self.viewer.setPhoto(pixmap)
            self.setup_bool = True
        else:
            self.viewer.update_photo(pixmap)
        self.update_label()

    def update_label(self):
        ## show current number of blobs
        self.label.setText("Number of objects is " + str(self.count()))



    def count(self):
        number = 0
        for i in self.keypoints[0:]:
            number = number + 1
        return number
        # return len(self.contoursrs)

    def set_detector(self):
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = False
        # params.minArea = 1
        # params.maxArea = 100000

        params.minDistBetweenBlobs = 0

        params.filterByCircularity = False
        # params.minCircularity = 0.1
        # params.maxCircularity = 1
        params.filterByConvexity = False
        # params.minConvexity = 0.1

        params.filterByInertia = False
        self.detector.empty()
        self.detector = cv2.SimpleBlobDetector_create(params)


    def process_image(self):
        ## find contours of the image
        im = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        _, im = cv2.threshold(im, 10, 255, cv2.THRESH_OTSU)
        im =cv2.bitwise_not(im)
        self.keypoints = list(self.detector.detect(im))
        # cv2.imwrite("Screen Shot 1401-02-15 at 16.47.27.png", cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
        # if not self.is_scaled:
        #     contours1, _ = cv2.findContours(image=im, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        #     image1 = image.copy()
        #     cv2.drawContours(image=image1, contours=contours1, contourIdx=-1, color=(255, 255, 255), thickness=1,
        #                      lineType=cv2.LINE_AA)
        #     self.contours = contours1
        #     return cv2.resize(image1, (COUNTIMAGE_WIDTH, COUNTIMAGE_HEIGHT))
        # else:
        #     im = cv2.resize(im, (COUNTIMAGE_WIDTH, COUNTIMAGE_HEIGHT))
        #
        #     contours2, _ = cv2.findContours(image=im, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        #     image2 = cv2.resize(image, (COUNTIMAGE_WIDTH, COUNTIMAGE_HEIGHT))
        #     cv2.drawContours(image=image2, contours=contours2, contourIdx=-1, color=(255, 255, 255), thickness=1,
        #                      lineType=cv2.LINE_AA)
        #     self.contours = contours2
        #     return image2







    def check_point(self, point):
        ## check if a clicked point is in a certain blob then delete it and add the deleted keypoint to a list
        point = [int(point.x()), int(point.y())]
        point[0] *= self.image.shape[1] / COUNTIMAGE_WIDTH
        point[1] *= self.image.shape[0] / COUNTIMAGE_HEIGHT
        point = cv2.KeyPoint(point[0], point[1], 1)
        for k in self.keypoints[0:]:
            if cv2.KeyPoint_overlap(point, k) != 0:
                self.keypoints.remove(k)
                self.removeds.append(k)
                break
        # for c in self.contours:
        #     inside = cv2.pointPolygonTest(c, tuple(point), False)
        #     if  inside == 1 or inside == 0 :
        #         self.removed_contours.append(c)
        if len(self.removeds) == 1:
            self.undo_btn.setEnabled(True)
        self.show_image()




    #
    # def apply_mask(self):
    #     if self.is_scaled:
    #         mask = np.ones((COUNTIMAGE_HEIGHT, COUNTIMAGE_WIDTH))
    #     else:
    #         mask = np.ones(self.image.shape[:2], dtype="uint8")
    #     for c in self.removed_contours:
    #         cv2.drawContours(mask, [c], -1, 0, -1)
    #     if self.is_scaled:
    #         mask = cv2.resize(mask, (self.image.shape[1],self.image.shape[0]) )
    #         mask = np.where(mask>0, 1, 0)
    #     return self.image * mask[...,None].astype(np.uint8)


    def undo_deletion(self):
        ## return the last deleted keypoint to the main list
        self.keypoints.append(self.removeds.pop())
        if len(self.removeds) == 0:
            self.undo_btn.setEnabled(False)
        self.show_image()

    def apply_changes(self):
        self.close()