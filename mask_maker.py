#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cv2
import CircleFitting as cf
import numpy as np
import argparse


class Circle(object):
    def __init__(self, x, y, r):
        self.cx = x
        self.cy = y
        self.r = r

    def set_center(self, x, y):
        self.cx = x
        self.cy = y

    def set_radius(self, r):
        self.r = r

    def is_valid(self):
        res = (self.cx >= 0 and self.cy >= 0)
        res &= self.r > 0
        return res


class mask_maker(object):
    def __init__(self, img_in, img_out="mask.png"):
        self.circle = Circle(-1, -1, -1)
        self.X = []
        self.Y = []
        self.img_in = img_in
        self.img_out = img_out

    def mouse_cb(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.X.append(x)
            self.Y.append(y)

            if len(self.X) >= 3:
                (cxe, cye, re) = cf.CircleFitting(self.X, self.Y)
                cxe = int(cxe)
                cye = int(cye)
                re = int(re)
                print("estimated: Center=({}, {}), Radius {}".format(
                    cxe, cye, re))
                self.circle = Circle(cxe, cye, re)

    def draw_gui(self):
        raw = cv2.imread(self.img_in)
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.mouse_cb)
        cv2.moveWindow('image', 100, 200)
        # mask = np.full(raw.shape[:2], 255, dtype=raw.dtype)

        while (1):
            img = raw.copy()

            if self.circle.is_valid():
                img = cv2.circle(img, (self.circle.cx, self.circle.cy),
                                 radius=self.circle.r,
                                 color=(255, 0, 0),
                                 thickness=10)

                mask = np.full(raw.shape[:2], 0, dtype=raw.dtype)
                mask = cv2.circle(mask, (self.circle.cx, self.circle.cy),
                                  radius=self.circle.r,
                                  color=(255, 255, 255),
                                  thickness=-1)

            if len(self.X) > 0:
                for p in zip(self.X, self.Y):
                    img = cv2.circle(img,
                                     p,
                                     radius=3,
                                     color=(0, 0, 255),
                                     thickness=-1)

            cv2.imshow('image', img)
            key = cv2.waitKey(100) & 0xFF

            # gui close with 'esc' or 'q'
            if key == 27 or key == ord("q"):
                break
            elif key == ord('s'):
                if self.circle.is_valid():
                    print("save mask image: {}".format(self.img_out))
                    cv2.imwrite(self.img_out, mask)
                else:
                    print("Save failed !! At least 3 points needed")

        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input image path")
    parser.add_argument("--output", default="mask.png", help="output mask image path")
    args = parser.parse_args()

    img_in = args.input
    img_out = args.output
    m = mask_maker(img_in, img_out)
    m.draw_gui()
