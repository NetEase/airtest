#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np

def _cv2open(filename, arg=0):
    obj = cv2.imread(filename, arg)
    if obj == None:
        raise IOError('cv2 read file error:'+filename)
    return obj

def _show_image(filename, left_top, (w, h)):
    img = cv2.imread(filename)
    x, y = left_top
    cv2.rectangle(img, (x, y), (x+w, y+h), 255, 2)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def findall(search_file, image_file, threshold=0.7):
    '''
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        search_file(string): filename of search object
        image_file(string): filename of image to search on
        threshold: optional variable, to ensure the match rate should >= threshold

    Returns:
        A tuple like (x, y) or None if nothing found

    Raises:
        IOError: when file read error
    '''
    search = _cv2open(search_file)
    image  = _cv2open(image_file)

    w, h = search.shape[::-1]

    method = cv2.TM_CCOEFF_NORMED
    # method = cv2.TM_CCORR_NORMED

    res = cv2.matchTemplate(image, search, method)

    points = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        if max_val > threshold:
            # floodfill the already found area
            sx, sy = top_left
            for x in range(sx-w/2, sx+w/2):
                for y in range(sy-h/2, sy+h/2):
                    try:
                        res[y][x] = np.float32(-10000) # -MAX
                    except IndexError: # ignore out of bounds
                        pass
            # _show_image(image_file, top_left, (w, h))
            middle_point = (top_left[0]+w/2, top_left[1]+h/2)
            points.append(middle_point)
        else:
            break
    return points

if __name__ == '__main__':
    search_file = 'no.png'
    threshold = 0.3
    positions = findall(search_file, 'timer.png', threshold)
    if positions:
        w, h = cv2.imread(search_file, 0).shape[::-1]
        img = cv2.imread('timer.png')
        for (x, y) in positions: 
            cv2.rectangle(img, (x-w/2, y-h/2), (x+w/2, y+h/2), 255, 2)

        cv2.imshow('image',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        
        # from matplotlib import pyplot as plt
        # plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
        # plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        # plt.show()
