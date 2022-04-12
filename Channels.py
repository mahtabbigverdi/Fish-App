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
        self.alphas = {}
        self.betas = {}
        self.initial_thresh = {}
        self.thresholds = {}
        self.noises = {}
        self.deletions = {}

    def add_channel(self, name, imagePath):
        self.dictionary[name] = cv2.resize(cv2.imread(imagePath), (IMAGE_WIDTH, IMAGE_HEIGHT))
        self.dictionary[name] = np.where(self.dictionary[name] < 10, 0, self.dictionary[name])
        cv2.cvtColor(self.dictionary[name], cv2.COLOR_BGR2RGB, self.dictionary[name])
        self.alphas[name] = DEFAULT_ALPHA
        self.betas[name] = DEFAULT_BETA
        ret, _ = cv2.threshold(cv2.cvtColor(self.dictionary[name], cv2.COLOR_RGB2GRAY), 10, 255, cv2.THRESH_OTSU)
        self.thresholds[name] = int(ret)
        self.initial_thresh[name] = int(ret)
        self.noises[name] = 0

        self.deletions[name] = []

    def add_deletion(self, name, coords1, coord2):
        min_y = min(coords1.y(), coord2.y())
        min_x = min(coords1.x(), coord2.x())
        max_y = max(coords1.y(), coord2.y())
        max_x = max(coords1.x(), coord2.x())


        self.deletions[name].append((min_y, max_y, min_x, max_x))

    def apply_deletions(self, name, image):
        for coords in self.deletions[name]:
            image[coords[0]:coords[1], coords[2]:coords[3]] = 0
        return image



    def undo_deletion(self, name):
        if len(self.deletions[name]) > 0 :
            self.deletions[name].pop()
            return True
        else:
            return False





    def get_image(self, name):
        new_image = self.dictionary[name].copy()
        new_image = self.apply_deletions(name, new_image)
        if self.thresholds[name] != self.initial_thresh[name]:
            _, mask = cv2.threshold(cv2.cvtColor(new_image, cv2.COLOR_RGB2GRAY), self.thresholds[name],
                                    255, cv2.THRESH_BINARY)
            new_image = new_image * mask[..., None]
        new_image = cv2.addWeighted(new_image, self.alphas[name],
                                    np.zeros(self.dictionary[name].shape,
                                             self.dictionary[name].dtype), 0,
                                    self.betas[name])
        ## TODO
        new_image = np.where(new_image<= self.betas[name], 0, new_image )
        new_image = self.denoise(new_image, self.noises[name])

        return new_image

    def denoise(self, image, noise_value):
        im = image.copy()
        for i in range(noise_value):
            im = cv2.bilateralFilter(im, 5, 75, 75)
        return im

    def sum_channels(self, selected_colors):
        out = np.array([])
        for key in self.dictionary.keys():
            if key not in selected_colors:
                continue
            if out.size == 0:
                out = self.get_image(key).copy()
            else:
                out += self.get_image(key)
        return out


    def delete_channel(self, name):
        del self.dictionary[name]
        del self.noises[name]
        del self.betas[name]
        del self.alphas[name]
        del self.deletions[name]
        del self.initial_thresh[name]
        del self.thresholds[name]


