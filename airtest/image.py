#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import sys
import time
import math

MIN_MATCH_COUNT = 5
# Euclidean distance calculation
def distance(p1, p2):
    l2 = (p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1])
    return math.sqrt(l2)
# remove the duplicate element of the list
def reremove(list):
    ''' order preserving '''
    checked = []
    for e in list:
        if e not in checked:
            checked.append(e)
    return checked
# color hist based similarity calculation
def HistSimilarity(origin='origin.png',query='query.png'):
    img1 = cv2.imread(origin,1) # queryImage,gray
    img2 = cv2.imread(query,1) # originImage,gray
    try:
        if img1.ndim ==2 & img2.ndim ==2:
            hist1 = cv2.calcHist([img1],[0],None,[256],[0.0,255.0])
            hist2 = cv2.calcHist([img2],[0],None,[256],[0.0,255.0])
            retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_CORREL)
            elif img1.ndim ==3 & img2.ndim ==3:
            ''' R,G,B split '''
            b1,g1,r1 = cv2.split(img1)
            b2,g2,r2 = cv2.split(img2)
            hist_b1 = cv2.calcHist([b1],[0],None,[256],[0.0,255.0])
            hist_g1 = cv2.calcHist([g1],[0],None,[256],[0.0,255.0])
            hist_r1 = cv2.calcHist([r1],[0],None,[256],[0.0,255.0])
            hist_b2 = cv2.calcHist([b2],[0],None,[256],[0.0,255.0])
            hist_g2 = cv2.calcHist([g2],[0],None,[256],[0.0,255.0])
            hist_r2 = cv2.calcHist([r2],[0],None,[256],[0.0,255.0])
            retal_b = cv2.compareHist(hist_b1,hist_b2,cv2.cv.CV_COMP_CORREL)
            retal_g = cv2.compareHist(hist_g1,hist_g2,cv2.cv.CV_COMP_CORREL)
            retal_r = cv2.compareHist(hist_r1,hist_r2,cv2.cv.CV_COMP_CORREL)
            sum_bgr = retal_b+retal_g+retal_r
            retal = sum_bgr/3
        else:
            img1 = cv2.cvtColor(img1,cv2.cv.CV_RGB2Gray)
            img2 = cv2.cvtColor(img2,cv2.cv.CV_RGB2Gray)
            hist1 = cv2.calcHist([img1],[0],None,[256],[0.0,255.0])
            hist2 = cv2.calcHist([img2],[0],None,[256],[0.0,255.0])
            retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_CORREL)
    '''
	#retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_BHATTACHARYYA)#Bhattacharyya distance
	#retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_CORREL)#Correlation
	#retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_CHISQR)#Chi-Square
	#retal = cv2.compareHist(hist1,hist2,cv2.cv.CV_COMP_INTERSECT)#Intersection
    '''
        return retal
    except:
        return None
# SIFT or SURF based similarity calculation
def FeatureSimilarity(origin='origin.png',query='query.png'):
    img1 = cv2.imread(query,0) # queryImage,gray
    img2 = cv2.imread(origin,0) # originImage,gray
    ''' Initiate SIFT detector '''
    sift = cv2.SIFT()
    #surf = cv2.SURF()
    try:
        ''' find the keypoints and descriptors with SIFT '''
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
        '''
        #kp1, des1 = surf.detectAndCompute(img1,None)
        #kp2, des2 = surf.detectAndCompute(img2,None)
        '''
    except:
        return []
    kpnum1 = len(kp1)
    kpnum2 = len(kp2)
    print kpnum1,kpnum2
	if kpnum1 <= kpnum2:
        kpnum = kpnum1
    else:
        kpnum = kpnum2
    print kpnum
    if kpnum <= 0:
		retal = 0.0
		return retal
    ''' search the match keypoints '''
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
	
    good = []
    for m,n in matches:
        ''' threshold = 0.7 '''
        if m.distance < 0.7*n.distance: 
            good.append(m)
    kpnum_good = float(len(good))
    print "Good Num: ", kpnum_good
    retal = kpnum_good/kpnum
    return retal
def locate_image(orig,quer,outfile='debug.png',threshold=0.3):
    pt = locate_one_image(orig, quer, outfile, threshold)
    if pt:
        return [pt]
    return None

def locate_one_image(origin='origin.png',query='query.png',outfile='match.png',threshold=0.3):
    
    '''
    Locate one image position

    @param origin: string (target filename)
    @param query: string (image need to search)
    @param threshold: float (range [0, 1), the lower the more ease to match)
    @return None if not found, (x,y) point if found
    '''
    threshold = 1- threshold
    img1 = cv2.imread(query,0) # queryImage,gray
    img2 = cv2.imread(origin,0) # originImage,gray
    target_img = cv2.imread(origin,1) # originImage    
    # Initiate SIFT detector
    sift = cv2.SIFT()
    try:
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
    except:
        return None
    #search and match the 
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    thresh_num = len(kp1)
    print "thresh: ", thresh_num
    t = thresh_num*0.1
    ratio_num = int(thresh_num*0.1)
    if t > float(ratio_num+0.5):
        ratio_num += 1
    print ratio_num
    h,w = img1.shape
    print "h, w: ", h, w
    #store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < threshold*n.distance: # threshold = 0.7
            good.append(m)
    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #origin_img match keypoints
        r,c,d = dst_pts.shape
        if r < 1:
            print "NO MATCH POINT"
            return None
        for i in range(r):
            x = dst_pts[i][c-1][d-2]
            y = dst_pts[i][c-1][d-1]
            cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        row,col,dim = dst.shape
        #print row,col,dim
        if row < 1:
            print "NO MATCH POINT"
            cv2.imwrite(outfile,target_img)
            return None
        center = dst[row-1][col-1]
        for i in range(row-1):
            center += dst[i][col-1] 
        if row < 1:
            print "NO Match"
            return None
        else:
            center_x = int(center[0]/row)
            center_y = int(center[1]/row)
            if outfile:
                cv2.rectangle(target_img,(int(center_x-w/2),int(center_y-h/2)),(int(center_x+w/2),int(center_y+h/2)),(0,0,255),1,0)
                cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                cv2.imwrite(outfile,target_img)
            print "center point: ", center_x, center_y
            return [center_x, center_y]

    else:
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        print dst_pts
        row,col,dim = dst_pts.shape
        print row,col,dim
        if (row < 1) | (row < ratio_num):
            print "NO MATCH POINT"
            if outfile:
                cv2.imwrite(outfile,target_img)
            return None
        list_x = []
        list_y = []
        for i in range(row):
            x = dst_pts[i][col-1][dim-2]
            y = dst_pts[i][col-1][dim-1]
            list_x.append(int(x))
            list_y.append(int(y))
            cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
        #duplicate removal
        rlist_x = reremove(list_x)
        rlist_y = reremove(list_y)
        center_sum_x = 0
        center_sum_y =0
        count = 0
        if len(rlist_x) < 1:
            print "NO Match"
            if outfile:
                cv2.imwrite(outfile,target_img)
            return None
        for i in range(len(rlist_x)):
            center_sum_x += rlist_x[i]
            center_sum_y += rlist_y[i]
            count += 1
        center_x = int(center_sum_x/count)
        center_y = int(center_sum_y/count)
        temp = [center_x,center_y]
        dist = []
        max = 0
        rcenter = [0,0]
        rcount = 0
        for i in range(count):
            #dis = abs(center_x-rlist_x[i])+abs(center_y-rlist_y[i])
            dis = distance(temp,[rlist_x[i],rlist_y[i]])
            if max < dis:
                max = dis
            dist.append(dis)
        for i in range(count):
            if count <= 2:
				rcenter[0] += rlist_x[i]
				rcenter[1] += rlist_y[i]
				rcount += 1
            else:
                if dist[i] < max:
                   rcenter[0] += rlist_x[i]
                   rcenter[1] += rlist_y[i]
                   rcount += 1
        if rcount < 1:
            print "NO Match"
            if outfile:
                cv2.imwrite(outfile,target_img)
            return None
        else:
            center_x = int(rcenter[0]/rcount)
            center_y = int(rcenter[1]/rcount)
            if outfile:
                cv2.rectangle(target_img,(int(center_x-w/2),int(center_y-h/2)),(int(center_x+w/2),int(center_y+h/2)),(0,0,255),1,0)
                cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                cv2.imwrite(outfile,target_img)
            print "center point: ", center_x, center_y
            return [center_x, center_y]

                

if __name__ == '__main__':
    starttime = time.clock()
    pts = locate_image('testdata/target.png','testdata/query.png','testdata/debug.png',0.3)
    endtime = time.clock()
    print endtime-starttime
    print "center point: ", pts
    if len(pts) < 1:
        print "Match Failure"
        exit(0)
    center_x = pts[0][0]
    center_y = pts[0][1]
    point = []
    #read the location information of the object in the origin image
    with open('testdata/data.txt','r') as f:
        for line in f:
            point.append(map(float,line.split(',')))
        print point
    pt = point[0]
    #object top_left coordinate
    topleft_x = int(pt[0])
    topleft_y = int(pt[1])
    #print topleft_x, topleft_y
    #object bottom_right corrdinate
    bottomright_x = int(pt[2])
    bottomright_y = int(pt[3])
    #print bottomright_x, bottomright_y
    if (topleft_x <= center_x & center_x <= bottomright_x) & (topleft_y <= center_y & center_y <= bottomright_y):
        print "Match Successfully !!!"
    else:
        print "Match Failure !!!"
    
