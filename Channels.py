import cv2
import numpy as np
from Constants import *



class Channels():

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Channels, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.dictionary = {}
        self.HShift = {}
        self.VShift = {}
        self.invert_mode = False
        self.move_deletions = {}
        self.move_changes = {}

    def add_channel(self, name, imagePath):
        ## open and resize image
        self.dictionary[name] = cv2.resize(cv2.imread(imagePath), (IMAGE_WIDTH, IMAGE_HEIGHT),
                                           interpolation=cv2.INTER_AREA)
        ## covert image from BGR to RGb
        self.dictionary[name] = cv2.cvtColor(self.dictionary[name], cv2.COLOR_BGR2RGB)

        # find threshold of image after applying otsu on grayscaled image
        ret, _ = cv2.threshold(cv2.cvtColor(self.dictionary[name], cv2.COLOR_RGB2GRAY), 10, 1, cv2.THRESH_OTSU)
        _, mask = cv2.threshold(cv2.cvtColor(self.dictionary[name], cv2.COLOR_RGB2GRAY), ret,
                                1, cv2.THRESH_BINARY)

        ## mask the image with the threshold
        self.dictionary[name] = self.dictionary[name] * mask[..., None]

        ## for moving a channel in different direction, we add MAX_VSHIFT black pixels in both top and bottom of the channel, and MAX_HSHIFT pixels
        # in right and left of the channel
        black = np.zeros((IMAGE_HEIGHT + MAX_VSHIFT * 2, IMAGE_WIDTH + MAX_HSHIFT * 2, 3)).astype(np.uint8)
        black[MAX_VSHIFT: MAX_VSHIFT + IMAGE_HEIGHT, MAX_HSHIFT: MAX_HSHIFT + IMAGE_WIDTH] = self.dictionary[name]
        self.dictionary[name] = black

        ## At first and insertion phase, we have no vertical/horizontal shifts
        self.HShift[name] = 0
        self.VShift[name] = 0

        ## At insertion phase we have no changed parts or sections in the channel
        self.move_changes[name] = []
        self.move_deletions[name] = []

    def StartInvertMode(self):
        self.invert_mode = True

    def EndInvertMode(self):
        self.invert_mode = False

    def get_invert_dapi(self, other=np.array([])):
        ## invert the blue channel of the Dapi Image
        inverted = 255 - self.get_image("Dapi")[:, :, 2]
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2RGB)
        # if other.size != 0:
        #     ## find colored parts in different signals and blacken their backgrounds instead of white
        #     other_mask = np.where(cv2.cvtColor(other, cv2.COLOR_RGB2GRAY) > 0, 1, 0)
        #     print(np.unique(other_mask))
        #     other_mask = 1 - other_mask
        #     print(np.unique(other_mask))
        #     inverted = inverted * other_mask[..., None].astype(np.uint8)
        return inverted

    def change_channel(self, name, changed_image, begin_x, begin_y, width, height):
        ## find the right coordinates considering added pixels or black paddings
        h_start = MAX_HSHIFT - self.HShift[name] + begin_x
        h_end = MAX_HSHIFT - self.HShift[name] + begin_x + width
        v_start = MAX_VSHIFT - self.VShift[name] + begin_y
        v_end = MAX_VSHIFT - self.VShift[name] + begin_y + height
        self.dictionary[name][v_start:v_end, h_start:h_end] = changed_image

    def denoise(self, image, noise_value):
        im = image.copy()
        for i in range(noise_value):
            im = cv2.bilateralFilter(im, 5, 75, 75)
        return im

    def get_image(self, name):
        ## the output of this function is a channel with all needed changes and shifts
        output_image = self.dictionary[name].copy()
        ## aply tempral changes while moving a part of image
        if len(self.move_deletions[name]) != 0:
            output_image[self.move_deletions[name][0]:self.move_deletions[name][1],
            self.move_deletions[name][2]:self.move_deletions[name][3]] = np.zeros(
                (self.move_deletions[name][1] - self.move_deletions[name][0],
                 self.move_deletions[name][3] - self.move_deletions[name][2], 3))
        if len(self.move_changes[name]) != 0:
            output_image[self.move_changes[name][0]:self.move_changes[name][1],
            self.move_changes[name][2]:self.move_changes[name][3]] = self.move_changes[name][4]

        ## apply shifts
        h_start = MAX_HSHIFT - self.HShift[name]
        h_end = h_start + IMAGE_WIDTH
        v_start = MAX_VSHIFT - self.VShift[name]
        v_end = v_start + IMAGE_HEIGHT
        return output_image[v_start:v_end, h_start:h_end]

    def sum_channels(self, selected_colors):
        out = np.array([])
        for key in self.dictionary.keys():
            if key == "Dapi" and self.invert_mode:
                continue
            if key not in selected_colors:
                continue
            if out.size == 0:
                out = self.get_image(key).copy()
            else:
                out += self.get_image(key)

        if self.invert_mode and "Dapi" in selected_colors and out.size != 0:
            out += self.get_invert_dapi(out).astype(np.uint8)
        elif self.invert_mode and "Dapi" in selected_colors and out.size == 0:
            out = self.get_invert_dapi().astype(np.uint8).copy()
        return out


    def delete_channel(self, name):
        del self.dictionary[name]
        del self.HShift[name]
        del self.VShift[name]
        del self.move_changes[name]
        del self.move_deletions[name]
        self.invert_mode = False

    def add_move_delete(self, name, begin_x, begin_y, width, height):
        ## save the section that a user wants to move to black it further
        h_start = MAX_HSHIFT - self.HShift[name] + begin_x
        h_end = MAX_HSHIFT - self.HShift[name] + begin_x + width
        v_start = MAX_VSHIFT - self.VShift[name] + begin_y
        v_end = MAX_VSHIFT - self.VShift[name] + begin_y + height
        self.move_deletions[name] = [v_start, v_end, h_start, h_end]

    def add_move_change(self, name, moved_part, begin_x, begin_y, width, height):
        ## save the new coordinates that the changed part has moved to
        h_start = MAX_HSHIFT - self.HShift[name] + begin_x
        h_end = MAX_HSHIFT - self.HShift[name] + begin_x + width
        v_start = MAX_VSHIFT - self.VShift[name] + begin_y
        v_end = MAX_VSHIFT - self.VShift[name] + begin_y + height
        self.move_changes[name] = [v_start, v_end, h_start, h_end, moved_part]

    def apply_shift(self, name, horizontal_shift, vertical_shift):
        ## edit shifts in the "whole" move mode
        self.HShift[name] += horizontal_shift
        self.VShift[name] += vertical_shift
        if self.HShift[name] < - MAX_HSHIFT:
            self.HShift[name] = -MAX_HSHIFT
        elif self.HShift[name] > MAX_HSHIFT:
            self.HShift[name] = MAX_HSHIFT

        if self.VShift[name] < -MAX_VSHIFT:
            self.VShift[name] = -MAX_VSHIFT
        elif self.VShift[name] > MAX_VSHIFT:
            self.VShift[name] = MAX_VSHIFT

    def reset_shift(self, name):
        self.HShift[name] = 0
        self.VShift[name] = 0

    def reset_move_change(self, name):
        ## after finishing moving a selected section, we have to delete the values for the next change
        self.move_deletions[name] = []
        self.move_changes[name] = []

    def accept_move_change(self, name):
        ## values in move_changes[name] and move_deletions[name] are temporal and for applying and accepting them on image we have to change the image
        self.dictionary[name][self.move_deletions[name][0]:self.move_deletions[name][1],
        self.move_deletions[name][2]:self.move_deletions[name][3]] = np.zeros(
            (self.move_deletions[name][1] - self.move_deletions[name][0],
             self.move_deletions[name][3] - self.move_deletions[name][2], 3))
        self.dictionary[name][self.move_changes[name][0]:self.move_changes[name][1],
        self.move_changes[name][2]:self.move_changes[name][3]] = self.move_changes[name][4]
        ## reset changes
        self.reset_move_change(name)
