#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

def _noise(img):
    ''' noise the black area, but a little slower '''
    tnx, tny = img.shape
    for x in range(tnx):
        for y in range(tny):
            if img[x, y] == 0:
                img[x,y] = random.randint(0, 255)
    return img


def _siftMatchTest(img1, img2):
    # descriptors
    sift = cv2.SIFT()
    k1, d1 = sift.detectAndCompute(img1,None)
    k2, d2 = sift.detectAndCompute(img2,None)
    # k1, d1 = descriptor.compute(img1, kp1)
    # k2, d2 = descriptor.compute(img2, kp2)

    print '#keypoints in image1: %d, image2: %d' % (len(d1), len(d2))

    # match the keypoints
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(d1,d2, k=2)
    # matches = matcher.match(d1, d2)

    # visualize the matches
    print '#matches:', len(matches)
    dist = [m.distance for m,n in matches]

    print 'distance: min: %.3f' % min(dist)
    print 'distance: mean: %.3f' % (sum(dist) / len(dist))
    print 'distance: max: %.3f' % max(dist)

    # threshold: half the mean
    thres_dist = (sum(dist) / len(dist)) * 0.5

    # keep only the reasonable matches
    sel_matches = [m for m,n in matches if m.distance < thres_dist]

    print '#selected matches:', len(sel_matches)

    # #####################################
    # visualization
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    view = np.zeros((max(h1, h2), w1 + w2, 3), np.uint8)
    view[:h1, :w1, 0] = img1
    view[:h2, w1:, 0] = img2
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]

    for m in sel_matches:
        # draw the keypoints
        # print m.queryIdx, m.trainIdx, m.distance
        color = tuple([np.random.randint(0, 255) for _ in xrange(3)])
        cv2.line(view, (int(k1[m.queryIdx].pt[0]), int(k1[m.queryIdx].pt[1])) , (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)


    cv2.imshow("view", view)
    cv2.waitKey()


def _matchTemplatePixel(image, templ):
    inx, iny = image.shape
    tnx, tny = templ.shape
    total = tnx*tny
    canvas = np.zeros((inx-tnx+1, iny-tny+1), np.float32)
    for i in range(inx-tnx+1):
        for j in range(iny-tny+1):
            count = 0
            for x in range(tnx):
                for y in range(tny):
                    if image.item(x+i, y  +j) == templ.item(x, y):
                        count += 1
            score = float(count)/total
            canvas[i][j] = np.float32(score)
    return canvas