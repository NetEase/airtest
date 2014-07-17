#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
2014/07/16 jiaqianghuai: 融合了特征匹配和模板匹配算法
'''

__author__ = 'hzjiaqianghuai,hzsunshx'
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
    #print kpnum1,kpnum2
    if kpnum1 <= kpnum2:
        kpnum = kpnum1
    else:
        kpnum = kpnum2
    #print kpnum
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
    #print "Good Num: ", kpnum_good
    retal = kpnum_good/kpnum
    return retal
def imgprocess(img,ratio):
    h = img.shape[0]
    w = img.shape[1]
    h_t = int(h*ratio)
    w_t = int(w*ratio)
    #print "h_t: %d, w_t: %d" % (h_t,w_t)
    h_b = h-h_t
    w_b = w-w_t
    for i in range(h):
        for j in range(w):
            if (img.ndim ==2) & ((i < h_t) | (j < w_t) | (h_b < i) | (w_b < j)):
                if 200 < img[i,j]:
                    img[i,j] = 0
            elif (img.ndim ==3) & ((i < h_t) | (j < w_t) | (h_b < i) | (w_b < j)):
                graylevel = int((img[i,j,0]+img[i,j,1]+img[i,j,2])/3)
                if 200 < graylevel:
                    img[i,j,0] = 0
                    img[i,j,1] = 0
                    img[i,j,2] = 0
    return img
def copyimg(center,w,h,target_img):
    center_x = center[0]
    center_y = center[1]
    topleft_x = int(center_x-w)
    topleft_y = int(center_y-h)
    #print "tx, ty: ", topleft_x, topleft_y
    if topleft_x < 0:
        topleft_x = 0
    if topleft_y < 0:
        topleft_y = 0
    #print "ndim: ",target_img.ndim
    rect_img = np.zeros((h*2,w*2),target_img.dtype)
    if target_img.ndim == 2:
        for i in range(h*2):
            ty = topleft_y+i
            if target_img.shape[0] <= ty:
                ty = target_img.shape[0]-1
            for j in range(w*2):
                tx = topleft_x+j
                if target_img.shape[1] <= tx:
                    tx = target_img.shape[1]-1
                rect_img[i][j] = target_img[ty][tx]
    elif target_img.ndim == 3:
        for i in range(h*2):
            ty = topleft_y+i
            for j in range(w*2):
                tx = topleft_x+j
                if target_img.shape[0] <= ty:
                    ty = target_img.shape[0]-1
                if target_img.shape[1] <= tx:
                    tx = target_img.shape[1]-1
                rect_img[i][j][0] = target_img[ty][tx][0]
                rect_img[i][j][1] = target_img[ty][tx][1]
                rect_img[i][j][2] = target_img[ty][tx][2]
    return rect_img
# template match function
def templatematch(target_img,query_img,value,situ,center):
    h_query = query_img.shape[0]
    w_query = query_img.shape[1]
    #print "w_query:%d, h_query:%d" % (w_query,h_query)
    w_temp = int(w_query/1)
    h_temp = int(h_query/1)
    #print "w2:%d, h2:%d" % (w_temp,h_temp)
    size = (w_temp,h_temp)
    temp = cv2.resize(query_img,size,cv2.cv.CV_INTER_LINEAR)
    h_target = target_img.shape[0]
    w_target = target_img.shape[1]
    #print "w_target:%d, h_target:%d" % (w_target,h_target)
    width=w_target-w_temp+1
    height=h_target-h_temp+1
    if width < 0 | height < 0:
		return None
    t_ret, t_thresh = cv2.threshold(target_img,200,255,cv2.THRESH_TOZERO)
    q_ret, q_thresh = cv2.threshold(query_img,200,255,cv2.THRESH_TOZERO)
    #result=np.zeros((width,height),np.uint8)
    #cv.MatchTemplate(image,template, result,cv.CV_TM_SQDIFF_NORMED)
    #result = cv2.matchTemplate(target_img,temp,cv2.cv.CV_TM_SQDIFF_NORMED)
    result = cv2.matchTemplate(t_thresh,q_thresh,cv2.cv.CV_TM_CCORR_NORMED)
    (min_val,max_val,minloc,maxloc)=cv2.minMaxLoc(result)
    #(x,y)=minloc
    (x,y)=maxloc
    if len(center):
        re_x = int(x+center[0]-w_temp/2)
        re_y = int(y+center[1]-h_temp/2)
    else:
        re_x = int(x+w_temp/2)
        re_y = int(y+h_temp/2)
    maxloc = [re_x,re_y]
    value.append(max_val)
    situ.append(maxloc)
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
    num1 = len(kp1)
    num2 = len(kp2)
    #search and match the 
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    thresh_num = len(kp1)
    #print "thresh: ", thresh_num
    t = thresh_num*0.1
    ratio_num = int(thresh_num*0.1)
    if t > float(ratio_num+0.5):
        ratio_num += 1
    #print ratio_num
    h,w = img1.shape
    #print "h, w: ", h, w
    #store all the good matches as per Lowe's ratio test.
    good = []
    kp2_xy = []
    for m,n in matches:
        kp2_xy.append(kp2[m.trainIdx].pt)
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
            #print "NO MATCH POINT"
            cv2.imwrite(outfile,target_img)
            return None
        center = [0,0]
        count = 0
        for i in range(row):
            if (dst[i][col-1][0] < target_img.shape[1]) & (0 <= dst[i][col-1][0]) & (dst[i][col-1][1] < target_img.shape[0]) & (0 <=dst[i][col-1][1]):
                center += dst[i][col-1]
                count += 1
                cv2.circle(target_img, (dst[i][col-1][0], dst[i][col-1][1]), 2, (255, 0, 255), -1)
        if count < 1:
            #print "NO Match"
            return None
        else:
            center_x = int(center[0]/count)
            center_y = int(center[1]/count)
            if outfile:
                cv2.rectangle(target_img,(int(center_x-w/2),int(center_y-h/2)),(int(center_x+w/2),int(center_y+h/2)),(0,0,255),1,0)
                cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                cv2.imwrite(outfile,target_img)
            #print "center point: ", center_x, center_y
            return [center_x, center_y]

    else:
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #print dst_pts
        row,col,dim = dst_pts.shape
        #print row,col,dim
        if (row < 1) | (row < ratio_num):
            print "ReMatch"
            re_dst_pts = np.float32([ kp2_xy[m] for m in range(len(kp2_xy)) ]).reshape(-1,1,2)
            re_r,re_c,re_d = re_dst_pts.shape
            temp = imgprocess(img1,0.1)
            if re_r:
                value = []
                situ = []
                for i in range(re_r):
                    center = re_dst_pts[i][re_c-1]
                    #print "point: ", center
                    rect_img = copyimg(center,w,h,img2)
                    templatematch(rect_img,temp,value,situ,center)
                    #print "i is: ", i
                max = value[re_r-1]
                k = re_r-1
                for i in range(re_r-1):
                    #print "value: ", value[i]
                    if max < value[i]:
                        max = value[i]
                        k = i
                #print k, max
                #print "Re_center: ", situ[k]
                if (max < 0.6) & (10 < num1):
                    center = []
                    value = []
                    situ = []
                    templatematch(img2,temp,value,situ,center)
                    #print "value", value
                    if value[0] < 0.7: #template similarity
                        return None
                    else:
                        center_x = situ[0][0]
                        center_y = situ[0][1]
                else:
                    center_x = situ[k][0]
                    center_y = situ[k][1]
            else:
                center = []
                value = []
                situ = []
                templatematch(img2,temp,value,situ,center)
                #print "value", value
                if value[0] < 0.7: #template similarity
                    return None
                else:
                    center_x = situ[0][0]
                    center_y = situ[0][1]
            if outfile:
                cv2.rectangle(target_img,(int(center_x-w/2),int(center_y-h/2)),(int(center_x+w/2),int(center_y+h/2)),(0,0,255),1,0)
                cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                cv2.imwrite(outfile,target_img)
            return [center_x,center_y]
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
            #print "NO Match"
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
            #print "NO Match"
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
            #print "center point: ", center_x, center_y
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

