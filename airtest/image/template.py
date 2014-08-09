#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

def _cv2open(filename, arg=0):
    obj = cv2.imread(filename, arg)
    if obj == None:
        raise IOError('cv2 read file error:'+filename)
    return obj

def find(search_file, image_file, threshold=0.8):
    '''
    Locate image position

    same as findall, except without arg maxcnt
    '''
    point = findall(search_file, image_file, threshold, maxcnt=1)
    return point if point else None

def findall(search_file, image_file, threshold=0.8, maxcnt = 0):
    '''
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        search_file(string): filename of search object
        image_file(string): filename of image to search on
        threshold: optional variable, to ensure the match rate should >= threshold
        maxcnt: maximun count of searched points

    Returns:
        A tuple of found points ((x, y), ...)

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
    
        if max_val < threshold:
            break
        middle_point = (top_left[0]+w/2, top_left[1]+h/2)
        points.append(middle_point)
        if maxcnt and len(points) >= maxcnt:
            break
        # floodfill the already found area
        cv2.floodFill(res, None, max_loc, (-1000,), max_val-threshold+0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
    return points

if __name__ == '__main__':
    search_file = 'imgs/me.png'
    image_file = 'imgs/timer.png'
    threshold = 0.9
    positions = find(search_file, image_file, threshold)
    print 'point_count =', len(positions)
    if positions:
        w, h = cv2.imread(search_file, 0).shape[::-1]
        img = cv2.imread(image_file)

        import imgutils
        for (x, y) in positions: 
            img = imgutils.markPoint(img, (x, y))
        imgutils.showImage(img)
    else:
        print 'No points founded'
