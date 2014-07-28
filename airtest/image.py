#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
2014/07/26 jiaqianghuai: fix the code
'''

__author__ = 'hzjiaqianghuai,hzsunshx'
import time
import math

import numpy as np
import cv2
import os

MIN_MATCH_COUNT = 5
MIN_MATCH = 15
DEBUG = os.getenv('DEBUG') == 'true'

#path check
def path_check(img_path):
    if not os.path.exists(img_path):
        raise IOError(img_path + 'not exists')

#Euclidean distance calculation
def distance(p1, p2):
    l2 = (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])
    return math.sqrt(l2)

#remove the duplicate element of the list
def reremove(list):
    checked = []
    for e in list:
        if e not in checked:
            checked.append(e)
    return checked

def _sort_point_list(list):
    new_list = []
    num = len(list)
    for i in range(num-1):
        min = list[0][1]
        k = 0
        for j in range(1,len(list)):
            if (list[j][1] < min):
                min = list[j][1]
                k = j
        new_list.append(list[k])
        del list[k]
    new_list.append(list[0])
    return new_list

#write keypoints and descriptors into an array
def pickle_keypoints(keypoints,descriptors):
    i = 0
    temp_array = []
    for point in keypoints:
        temp = (point.pt,point.size,point.angle,point.response,point.octave,point.class_id,descriptors[i])
        i += 1
        temp_array.append(temp)
    return temp_array

#filter the keypoints and descriptors of the detected object
def unpickle_keypoints(array,center,w,h,shape):
    keypoints,descriptors = [],[]
    center_x = center[0]
    center_y = center[1]
    topleft_x = int(center_x-w)
    topleft_y = int(center_y-h)
    bottomright_x = int(center_x+w)
    bottomright_y = int(center_y+h)
    if topleft_x < 0:
        topleft_x = 0
    if topleft_y < 0:
        topleft_y = 0
    if shape[1] <= bottomright_x:
        bottomright_x = shape[1]-1
    if shape[0] <= bottomright_y:
        bottomright_y = shape[0]-1
    for point in array:
        x = int(point[0][0])
        y = int(point[0][1])
        if (x < topleft_x) | (y < topleft_y) | (bottomright_x < x) | (bottomright_y < y):
            temp_feature = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1],_angle=point[2],_response=point[3],_octave=point[4],_class_id=point[5])
            temp_descriptor = point[6]
            keypoints.append(temp_feature)
            descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)

# color hist based similarity calculation
def hist_similarity(img1,img2):
    try:
        if img1.ndim == 2 & img2.ndim == 2:
            hist1 = cv2.calcHist([img1], [0], None, [256], [0.0, 255.0])
            hist2 = cv2.calcHist([img2], [0], None, [256], [0.0, 255.0])
            retal = cv2.compareHist(hist1, hist2, cv2.cv.CV_COMP_CORREL)
        elif img1.ndim == 3 & img2.ndim == 3:
            ''' R,G,B split '''
            b1, g1, r1 = cv2.split(img1)
            b2, g2, r2 = cv2.split(img2)
            hist_b1 = cv2.calcHist([b1], [0], None, [256], [0.0, 255.0])
            hist_g1 = cv2.calcHist([g1], [0], None, [256], [0.0, 255.0])
            hist_r1 = cv2.calcHist([r1], [0], None, [256], [0.0, 255.0])
            hist_b2 = cv2.calcHist([b2], [0], None, [256], [0.0, 255.0])
            hist_g2 = cv2.calcHist([g2], [0], None, [256], [0.0, 255.0])
            hist_r2 = cv2.calcHist([r2], [0], None, [256], [0.0, 255.0])
            retal_b = cv2.compareHist(hist_b1, hist_b2, cv2.cv.CV_COMP_CORREL)
            retal_g = cv2.compareHist(hist_g1, hist_g2, cv2.cv.CV_COMP_CORREL)
            retal_r = cv2.compareHist(hist_r1, hist_r2, cv2.cv.CV_COMP_CORREL)
            sum_bgr = retal_b + retal_g + retal_r
            retal = sum_bgr / 3
        else:
            img1 = cv2.cvtColor(img1, cv2.cv.CV_RGB2GRAY)
            img2 = cv2.cvtColor(img2, cv2.cv.CV_RGB2GRAY)
            hist1 = cv2.calcHist([img1], [0], None, [256], [0.0, 255.0])
            hist2 = cv2.calcHist([img2], [0], None, [256], [0.0, 255.0])
            retal = cv2.compareHist(hist1, hist2, cv2.cv.CV_COMP_CORREL)
        return retal
    except:
        return None

# SIFT or SURF based similarity calculation
def re_feature_similarity(kp1, des1, kp2, des2):
    kpnum1 = len(kp1)
    kpnum2 = len(kp2)
    if kpnum1 <= kpnum2:
        kpnum = kpnum1
    else:
        kpnum = kpnum2
    if kpnum <= 0:
        retal = 0.0
        return retal
    matches = _search(des1, des2)
    good = []
    for m, n in matches:
        ''' threshold = 0.7 '''
        if m.distance < 0.7 * n.distance:
            good.append(m)
    kpnum_good = float(len(good))
    retal = kpnum_good / kpnum
    return retal,kpnum_good

# 查询图片边缘的像素赋值为0，主要是处理那些背景为透明的图片
def _img_process(img, ratio):
    h = img.shape[0]
    w = img.shape[1]
    h_t = int(h * ratio)
    w_t = int(w * ratio)
    h_b = h - h_t
    w_b = w - w_t
    for i in range(h):
        for j in range(w):
            if (img.ndim == 2) & ((i < h_t) | (j < w_t) | (h_b < i) | (w_b < j)):
                if 200 < img[i, j]:
                    img[i, j] = 0
            elif (img.ndim == 3) & ((i < h_t) | (j < w_t) | (h_b < i) | (w_b < j)):
                graylevel = int((img[i, j, 0] + img[i, j, 1] + img[i, j, 2]) / 3)
                if 200 < graylevel:
                    img[i, j, 0],img[i, j, 1],img[i, j, 2] = 0,0,0
    return img

def _img_zero(w,h,center,img):
    top_left_x = int(center[0]-w)
    top_left_y = int(center[1]-h)
    for i in range(h*2):
        y = top_left_y+i
        if img.shape[0] <= y:
            y = img.shape[0]-1
        for j in range(w*2):
            x = top_left_x + j
            if img.shape[1] <= x:
                x = img.shape[1]-1
            if img.ndim == 2:
                img[y,x] = 0
            elif img.ndim == 3:
                img[y,x,0],img[y,x,1],img[y,x,2] = 0,0,0
    return img

#image read
def _img_read(origin,query):
    img1 = cv2.imread(query, 0)  # queryImage,gray
    img2 = cv2.imread(origin, 0)  # originImage,gray
    query_img = cv2.imread(query, 1)  # queryImage
    target_img = cv2.imread(origin, 1)  # originImage
    return img1,img2,query_img,target_img

#rectangle multi_object
def _img_multi__rectangle(w,h,center_xy,target_img):
    for i in range(len(center_xy)):
        center_i = center_xy[i]
        if (0 < center_i[0] < target_img.shape[1]) & (0 < center_i[1] < target_img.shape[0]):
            topleft_x = int(center_i[0]-w*0.5)
            topleft_y = int(center_i[1]-h*0.5)
            bottomright_x = int(center_i[0]+w*0.5)
            bottomright_y = int(center_i[1]+h*0.5)
            if topleft_x < 0:
                topleft_x = 0
            if topleft_y < 0:
                topleft_y = 0
            if target_img.shape[1] <= bottomright_x:
                bottomright_x = target_img.shape[1]-1
            if target_img.shape[0] <= bottomright_y:
                bottomright_y = target_img.shape[0]-1
            cv2.rectangle(target_img,(topleft_x,topleft_y),(bottomright_x,bottomright_y),(0,0,255),1,0)
            cv2.circle(target_img, (int(center_i[0]), int(center_i[1])), 2, (0, 255, 0), -1)   

def _homography(h, w, kp1,kp2,good,target_img):
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    #origin_img match keypoints
    r, c, d = dst_pts.shape
    if r < 1:  #不存在匹配点
        return None
    for i in range(r):
        x = dst_pts[i][c - 1][d - 2]
        y = dst_pts[i][c - 1][d - 1]
        cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)  #最少需要4个match点
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)  #找到一个变换矩阵，从查询图片映射到检测图片
    return dst

#复制图像
def copyimg(center, w, h, target_img, num):
    center_x = center[0]
    center_y = center[1]
    topleft_x = int(center_x - w)
    topleft_y = int(center_y - h)
    if topleft_x < 0:
        topleft_x = 0
    if topleft_y < 0:
        topleft_y = 0
    if target_img.ndim == 2:
        rect_img = np.zeros((h * num, w * num), target_img.dtype)
        for i in range(h * num):
            ty = topleft_y + i
            if target_img.shape[0] <= ty:
                ty = target_img.shape[0] - 1
            for j in range(w * num):
                tx = topleft_x + j
                if target_img.shape[1] <= tx:
                    tx = target_img.shape[1] - 1
                rect_img[i][j] = target_img[ty][tx]
    elif target_img.ndim == 3:
        rect_img = np.zeros((h, w, 3), target_img.dtype)
        for i in range(h):
            ty = topleft_y + i
            for j in range(w):
                tx = topleft_x + j
                if target_img.shape[0] <= ty:
                    ty = target_img.shape[0] - 1
                if target_img.shape[1] <= tx:
                    tx = target_img.shape[1] - 1
                rect_img[i][j][0] = target_img[ty][tx][0]
                rect_img[i][j][1] = target_img[ty][tx][1]
                rect_img[i][j][2] = target_img[ty][tx][2]
    return rect_img

# template match function，这里加了图像灰度阈值处理
def templatematch(target_img, query_img, value, situ, center):
    h_query = query_img.shape[0]
    w_query = query_img.shape[1]
    w_temp = int(w_query / 1)
    h_temp = int(h_query / 1)
    size = (w_temp, h_temp)
    temp = cv2.resize(query_img, size, cv2.cv.CV_INTER_LINEAR)
    h_target = target_img.shape[0]
    w_target = target_img.shape[1]
    width = w_target - w_temp + 1
    height = h_target - h_temp + 1
    if width < 0 | height < 0:
        return None
    t_ret, t_thresh = cv2.threshold(target_img, 200, 255, cv2.THRESH_TOZERO)
    q_ret, q_thresh = cv2.threshold(query_img, 200, 255, cv2.THRESH_TOZERO)
    result = cv2.matchTemplate(t_thresh, q_thresh, cv2.cv.CV_TM_CCORR_NORMED)#cv2.cv.CV_TM_SQDIFF_NORMED
    (min_val, max_val, minloc, maxloc) = cv2.minMaxLoc(result)
    (x, y) = maxloc
    if len(center):
        re_x = int(x + center[0] - w_temp / 2)
        re_y = int(y + center[1] - h_temp / 2)
    else:
        re_x = int(x + w_temp / 2)
        re_y = int(y + h_temp / 2)
    maxloc = [re_x, re_y]
    value.append(max_val)
    situ.append(maxloc)

def origin_templatematch(target_img, query_img):
    h_query = query_img.shape[0]
    w_query = query_img.shape[1]
    h_target = target_img.shape[0]
    w_target = target_img.shape[1]
    width = w_target - w_query + 1
    height = h_target - h_query + 1
    if width < 0 | height < 0:
        return None
    result = cv2.matchTemplate(target_img, query_img, cv2.cv.CV_TM_SQDIFF_NORMED)
    (min_val, max_val, minloc, maxloc) = cv2.minMaxLoc(result)
    (x,y)=minloc
    return min_val,minloc

def siftextract(target_img):
    sift = cv2.SIFT()# Initiate SIFT detector
    kp, des = sift.detectAndCompute(target_img, None)# find the keypoints and descriptors with SIFT
    return kp, des

def _search(des1, des2): 
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    return matches

# SIFT + Homography
def _homography_match(h, w, kp1,kp2,des1,des2,good,img1,img2,target_img, outfile):
    dst = _homography(h, w, kp1,kp2,good,target_img)
    row, col, dim = dst.shape
    if row < 1:
        return None
    center = [0, 0]
    count = 0
    for i in range(row):
        if (int(dst[i][col - 1][0]) <= target_img.shape[1]) & (0 <= int(dst[i][col - 1][0])) & (
                    int(dst[i][col - 1][1]) <= target_img.shape[0]) & (0 <= int(dst[i][col - 1][1])): #表达式需要修改
            center += dst[i][col - 1]
            count += 1
            cv2.circle(target_img, (dst[i][col - 1][0], dst[i][col - 1][1]), 2, (255, 0, 255), -1)
    if ((count < 1) | (count < int(row * 0.5))):  #仿射变换得到的四个坐标，如果至少有两个坐标不在检测图片区域，说明匹配不成功
        return None
    else:
        center_x = int(center[0] / count)
        center_y = int(center[1] / count)
        rect_img = copyimg((center_x,center_y),w,h,img2,2) ######
        kp, des = siftextract(rect_img)
        value,kp_num = re_feature_similarity(kp, des, kp1, des1) #######
        if DEBUG:
            print "feature_match value: ", value
            print "kp_num: ", kp_num
        if (value >= 0.4) | ((kp_num <= 14) & (0.34 < value)) | (35 < kp_num) |((kp_num <= 5) & (len(kp1) <= (20*kp_num))):
            if outfile:
                cv2.rectangle(target_img,(int(center_x-w/2),int(center_y-h/2)),
                    (int(center_x+w/2),int(center_y+h/2)),(0,0,255),1,0)
                cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                cv2.imwrite(outfile,target_img)
            return [center_x, center_y]
        else:
            rect_img2 = copyimg((center_x,center_y),h,w,img2,2) ######
            kp, des = siftextract(rect_img2)
            value2,kp_num2 = re_feature_similarity(kp,des,kp1,des1) #######
            if DEBUG:
                print "feature_match value 2:  ", value2
                print "kp_num 2: ", kp_num2
            if ((0.32 < value2) | (35 < kp_num)) & (value < value2) & (kp_num < kp_num2):
                if outfile:
                    cv2.rectangle(target_img,(int(center_x-h/2),int(center_y-w/2)),
                        (int(center_x+h/2),int(center_y+w/2)),(0,0,255),1,0)
                    cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                    cv2.imwrite(outfile,target_img)
                return [center_x, center_y]
            else:
                return None

def _re_homsift_match(h,w,kp1,kp2,good,target_img,point_match):
    dst = _homography(h, w, kp1,kp2,good,target_img)
    row,col,dim = dst.shapel
    if row < 1:
        return None
    center = dst[row-1][col-1]
    for i in range(row-1):
        center += dst[i][col-1] 
    if row < 1:
        return None
    else:
        center_x = int(center[0]/row)
        center_y = int(center[1]/row)
        temp = (center_x, center_y)
        return [center_x, center_y]

def _re_detectAndmatch(kp1,des1,kp2,des2,val1,val2,disp,kp2_xy, img1, img2, query_img, target_img, outfile):
    h, w = img1.shape
    re_dst_pts = np.float32([kp2_xy[m] for m in range(len(kp2_xy))]).reshape(-1, 1, 2)
    re_r, re_c, re_d = re_dst_pts.shape
    if DEBUG:
        print "re_r: ", re_r
    num1 = len(kp1)
    num2 = len(kp2)
    temp = _img_process(img1, 0.1)
    if (re_r < 35):
        value, situ, num = [], [], []
        for i in range(re_r):
            center = re_dst_pts[i][re_c - 1]
            rect_img = copyimg(center, w, h, img2, 2)
            kp, des = siftextract(rect_img)
            tp,default = re_feature_similarity(kp,des,kp1,des1)
            num.append(tp)
            templatematch(rect_img, temp, value, situ, center)
        max = value[re_r - 1]
        k = re_r - 1
        for i in range(re_r - 1):
            if max < value[i]:
                max = value[i]
                k = i
        if DEBUG:
            print k, max, num[k]
        if (0.18 < num[k]):
            if (max <= 0.6) & (5 < num1):
                center, value, situ = [], [], []
                templatematch(img2, temp, value, situ, center)
                if value[0] < 0.7:  #template similarity
                    return None
                else:
                    center_x = situ[0][0]
                    center_y = situ[0][1]
                    rect_img = copyimg((center_x, center_y), w, h, target_img, 1)
                    value = hist_similarity(rect_img, query_img)
                    if (value < 0.03):
                        return None
            else:
                center_x = situ[k][0]
                center_y = situ[k][1]
                if (max < 0.9):
                    rect_img = copyimg((center_x, center_y), w, h, target_img, 1)
                    rect_img2 = copyimg((center_x, center_y), w, h, img2, 2)
                    val = hist_similarity(rect_img, query_img)
                    kp, des = siftextract(rect_img2)
                    val2,default = re_feature_similarity(kp,des,kp1,des1)
                    if (val < 0.03) | (val2 < 0.15):  #
                        return None
        else:
            if ((0.9 < max) & (0.09 < num[k])):
                center_x = situ[k][0]
                center_y = situ[k][1]
            else:
                return None
    else:
        if (num1 <= num2):
            if(val2 <= 0.15):
                return None
        else:
            if (num2 < 2):
                return None
            else: 
                val,default = re_feature_similarity(kp1,des1,kp2,des2)
                if (val <= 0.4):  ####0.15
                    return None
        if (val1[0] < 0.7) | ((num2*10) < num1):  #template similarity
            return None
        else:
            center_x = disp[0]
            center_y = disp[1]
    top_x = int(center_x - w / 2)
    top_y = int(center_y - h / 2)
    if (top_x < 0) | (top_y < 0):
        return None
    if outfile:
        cv2.rectangle(target_img, (int(center_x - w / 2), int(center_y - h / 2)),(int(center_x + w / 2), int(center_y + h / 2)), (0, 0, 255), 1, 0)
        cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
        cv2.imwrite(outfile, target_img)
    return [center_x, center_y]

def _refine_center(list_x, list_y,w,h):
    center_sum_x, center_sum_y, count = 0, 0, 0
    rlist_x = reremove(list_x)#duplicate removal
    rlist_y = reremove(list_y)
    if len(rlist_x) < 1:
        return None
    rx_len = len(rlist_x)
    ry_len = len(rlist_y)
    if rx_len == ry_len:
        x_list = rlist_x
        y_list = rlist_y
        for i in range(rx_len):
            center_sum_x += x_list[i]
            center_sum_y += y_list[i]
            count += 1
    else:
        x_list = list_x
        y_list = list_y
        for i in range(len(x_list)):
            center_sum_x += x_list[i]
            center_sum_y += y_list[i]
            count += 1
    center_x = int(center_sum_x / count)
    center_y = int(center_sum_y / count)
    temp = [center_x, center_y]
    dist = []
    index = []
    max, rcount,rcount1 = 0, 0, 0
    rcenter = [0, 0]
    for i in range(count):
        dis = distance(temp, [x_list[i], y_list[i]])#dis = abs(center_x-rlist_x[i])+abs(center_y-rlist_y[i])
        if max < dis:
            max = dis
        dist.append(dis)
    for i in range(count):
        if count <= 2:
            rcenter[0] += x_list[i]
            rcenter[1] += y_list[i]
            rcount += 1
            index.append(i)
        else:
            if dist[i] < max:
                rcenter[0] += x_list[i]
                rcenter[1] += y_list[i]
                rcount += 1
                index.append(i)
    if rcount < 1:
        return None
    else:
        x = int(rcenter[0]/rcount)
        y = int(rcenter[1]/rcount)
    length = len(index)
    for i in range(length):
        if (int(1.5*w) < (abs(x-x_list[index[i]]))) | (int(1.5*h) < (abs(y-y_list[index[i]]))):
            rcount1 = rcount1+1
    if rcount1 == rcount:
        return None
    else:
        return [x,y]

def _adjust_center(w,h,ratio_num,good_match_num,center_xy,point_match,target_img):
    re_center_xy = []
    re_center_xy.append(center_xy[0])
    length = len(point_match)
    point_xy = []
    point_xy.append(point_match[length-1])
    for i in range(length-1):
        count = 0
        for j in range(len(point_xy)):
            if (point_match[i][0]!= point_xy[j][0]) | (point_match[i][1]!= point_xy[j][1]):
                count = count+1
        if (count == len(point_xy)):
            point_xy.append(point_match[i])
    for i in range(len(center_xy)-1):
        sum_x = 0
        sum_y = 0
        k = 0
        for j in range(len(point_xy)):
            if ((abs(center_xy[i+1][0]-point_xy[j][0]) < int(w/2)) & (abs(center_xy[i+1][1]-point_xy[j][1]) < int(h/2)) & (0 < (center_xy[i+1][0]-int(w/2))) & 
                    (0 < (center_xy[i+1][1]-int(h/2))) & ((center_xy[i+1][0]+int(w/2)) < target_img.shape[1]) & ((center_xy[i+1][1]+int(h/2)) < target_img.shape[0])):
                sum_x += point_xy[j][0]
                sum_y += point_xy[j][1]
                k = k + 1
        print good_match_num
        if (ratio_num <= k) & (k > 0):
            x = int(sum_x/k)
            y = int(sum_y/k)
            re_center = [x, y]
            re_center_xy.append(re_center)
    new_center = _sort_point_list(re_center_xy)
    return new_center

# find the next object and its center
def _nextobject(w,h,match,kp1,kp2,center_xy,point_match,target_img):
    good = []
    for m,n in match:
        if m.distance < 0.9*n.distance: #0.95,0.9s
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        center = _re_homsift_match(h,w,kp1,kp2,good,target_img,point_match)
        if center:
            center_xy.append(center)
    else:
        if len(good) >= 2:
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            row,col,dim = dst_pts.shape
            if row < 1:
                if DEBUG:
                    print "NO MATCH POINT"
            else:
                for i in range(row):
                    x = dst_pts[i][col-1][dim-2]
                    y = dst_pts[i][col-1][dim-1]
                    cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
                    tem = [x, y]
                    point_match.append(tem)
                center = dst_pts[row-1][col-1]
                for i in range(row-1):
                    center += dst_pts[i][col-1] 
                if row < 1:
                    if DEBUG:
                        print "NO Match"
                else:
                    center_x = int(center[0]/row)
                    center_y = int(center[1]/row)
                    temp = [center_x,center_y]
                    center_xy.append(temp)
                    if DEBUG:
                        print center_x, center_y
        else:
            if DEBUG:
                print "Match Failure !!!"

def locate_image(orig, quer, outfile='DEBUG.png', threshold=0.3):
    pt = locate_one_image(orig, quer, outfile, threshold)
    if pt:
        return [pt]
    return None

def locate_one_image(origin, query, outfile='match.png', threshold=0.3):
    '''
    Locate one image position

    @param origin: string (target filename)
    @param query: string (image need to search)
    @param threshold: float (range [0, 1), the lower the more ease to match)
    @return None if not found, (x,y) point if found
    '''
    path_check(origin)
    path_check(query)
    img1,img2,query_img,target_img = _img_read(origin,query)
    threshold = 1 - threshold
    h, w = img1.shape
    '''提前过滤，排除那些肯定不存在查询图片的测试图片'''
    v1 = []
    s1 = []
    templatematch(img2, img1, v1, s1, [])  #全局模板匹配
    c1 = s1[0]
    print v1
    rect = copyimg((c1[0], c1[1]), w, h, img2, 2)  #复制潜在匹配区域
    try:
        # find the keypoints and descriptors with SIFT
        kp1, des1 = siftextract(img1)
        kp3, des3 = siftextract(rect)
        num1 = len(kp1)
        num3 = len(kp3)
    except:
        return None
    val2 = 1.0
    if num1 <= num3:
        val2,default = re_feature_similarity(kp1, des1, kp3, des3)
        if DEBUG:
            print "val: ", val2
        if (int(num1*10) <= num3) and (MIN_MATCH < num1):
            if (val2 == 0.0): 
                return None
    if num3 == 0:
        return None
    try:
        kp2, des2 = siftextract(img2)
        num2 = len(kp2)
        if num2 < num1:
            return None
    except:
        return None
    ratio_num = int(num1 * 0.1)
    '''store all the good matches as per Lowe's ratio test.'''
    matches = _search(des1, des2)
    good,kp2_xy = [],[]
    for m, n in matches:
        kp2_xy.append(kp2[m.trainIdx].pt)
        if m.distance < threshold * n.distance:  # threshold = 0.7
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:  #good matches的数量超过给定阈值，则进行Homography
        center = _homography_match(h, w, kp1,kp2,des1,des2, good, img1,img2,target_img, outfile)
        if DEBUG:
            print "center: ",center
        return center
    else:
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        row, col, dim = dst_pts.shape
        if (row < 1) | (row < ratio_num) | ((row == 1) & (ratio_num == 1)):
            center = _re_detectAndmatch(kp1,des1,kp3,des3,v1,val2,c1,kp2_xy, img1, img2, query_img, target_img, outfile)
            if DEBUG:
                print "center: ",center
            return center
        else:
            list_x, list_y = [], []
            for i in range(row):
                x = dst_pts[i][col - 1][dim - 2]
                y = dst_pts[i][col - 1][dim - 1]
                list_x.append(int(x))
                list_y.append(int(y))
                cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
            newcenter = _refine_center(list_x, list_y,w,h)
            if newcenter:
                center_x = newcenter[0]
                center_y = newcenter[1]
                top_x = int(center_x - w / 2)
                top_y = int(center_y - h / 2)
                if (top_x < 0) & (top_y < 0):
                    return None
                if outfile:
                    cv2.rectangle(target_img, (int(center_x - w / 2), int(center_y - h / 2)),
                              (int(center_x + w / 2), int(center_y + h / 2)), (0, 0, 255), 1, 0)
                    cv2.circle(target_img, (center_x, center_y), 2, (0, 255, 0), -1)
                    cv2.imwrite(outfile, target_img)
                if DEBUG:
                    print "center: ",[center_x, center_y]
                return [center_x, center_y]

def locate_more_image(origin,query,outfile='match.png',threshold=0.3,object_num=7):

    '''
    Locate multi_object image position

    @param origin: string (target filename)
    @param query: string (image need to search)
    @param threshold: float (range [0, 1), the lower the more ease to match)
    @return None if not found, (x,y) point list if found
    '''
    path_check(origin)
    path_check(query)
    img1,img2,query_img,target_img = _img_read(origin,query)
    threshold = 1-threshold
    # find the keypoints and descriptors with SIFT
    kp1, des1 = siftextract(img1)
    kp2, des2 = siftextract(img2)
    '''store all the good matches as per Lowe's ratio test.'''
    matches = _search(des1, des2)
    # store all the good matches as per Lowe's ratio test.
    good,center_xy, point_match= [],[],[]  
    for m,n in matches:
        if m.distance < threshold*n.distance:
            good.append(m)
    h,w = img1.shape
    ratio_num = int(len(kp1)*0.1)
    if len(good)>MIN_MATCH_COUNT:
        center = _re_homsift_match(h,w,kp1,kp2,good,target_img,point_match)
        center_xy.append(center)        
    else:
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        row,col,dim = dst_pts.shape
        if (1 <= row):
            for i in range(row):
                x = dst_pts[i][col-1][dim-2]
                y = dst_pts[i][col-1][dim-1]
                cv2.circle(target_img, (int(x), int(y)), 2, (255, 0, 0), -1)
                point_match.append([x, y])
            center = dst_pts[row-1][col-1]
            for i in range(row-1):
                center += dst_pts[i][col-1] 
            if (row < 1) | (row < ratio_num):
                if DEBUG:
                    print "NO Match"
            else:
                center_x = int(center[0]/row)
                center_y = int(center[1]/row)
                temp = [center_x,center_y]
                center_xy.append(temp)
                if DEBUG:
                    print center_x, center_y
    if len(center_xy) < 1:
        return None
    else:
        for i in range(1,object_num):
            center = center_xy[-1]
            array = pickle_keypoints(kp2,des2)
            kp2,des2 = unpickle_keypoints(array,center,w,h,target_img.shape)
            matches = _search(des1, des2)
            _nextobject(w,h,matches,kp1,kp2,center_xy,point_match,target_img)
        re_center_xy = _adjust_center(w,h,ratio_num,good_match_num,center_xy,point_match,target_img)
        _img_multi__rectangle(w,h,re_center_xy,target_img)                 
        if outfile:
            cv2.imwrite(outfile,target_img)
        return re_center_xy

def locate_more_image_template(origin,query,outfile='match.png',object_num=5):
    path_check(origin)
    path_check(query)
    img1,img2,query_img,target_img = _img_read(origin,query)
    h = img1.shape[0]
    w = img1.shape[1]
    center= []
    minval, minloc = origin_templatematch(img2, img1)
    center.append([int(minloc[0]+w/2),int(minloc[1]+h/2)])
    temp = img2
    if object_num == 0:
        while (1):
                temp = _img_zero(w,h,center[-1],temp)
                minval, minloc = origin_templatematch(temp, img1)
                if 0.07 < minval:
                    break
                center.append([int(minloc[0]+w/2),int(minloc[1]+h/2)])
    else:        
        for i in range(object_num-1): 
            temp = _img_zero(w,h,center[-1],temp)
            minval, minloc = origin_templatematch(temp, img1)
            center.append([int(minloc[0]+w/2),int(minloc[1]+h/2)])
    if outfile:
        _img_multi__rectangle(w,h,center,target_img) 
        cv2.imwrite(outfile,target_img)
    new_center = _sort_point_list(center)
    return new_center

if __name__ == '__main__':
    starttime = time.clock()
    pts = locate_image('testdata/target.jpg', 'testdata/query.png', 'testdata/DEBUG.png', 0.3)
    #multi_center = locate_more_image('testdata/target.png', 'testdata/query.png', 'testdata/DEBUG.png', 0.3, 1)
    #pts = locate_more_image_template('testdata/target.jpg', 'testdata/query.png', 'testdata/DEBUG.png',0)
    endtime = time.clock()
    print "time: ", endtime - starttime
    print "center point: ", pts
    if pts:
        center_x = pts[0][0]
        center_y = pts[0][1]
        point = []
        #read the location information of the object in the origin image
        with open('testdata/data.txt', 'r') as f:
            for line in f:
                point.append(map(float, line.split(',')))
        pt = point[0]
        topleft_x = int(pt[0])
        topleft_y = int(pt[1])
        bottomright_x = int(pt[2])
        bottomright_y = int(pt[3])
        if (topleft_x <= center_x & center_x <= bottomright_x) & (topleft_y <= center_y & center_y <= bottomright_y):
            print "Match Successfully !!!"
        else:
            print "Match Failure !!!"
    else:
        print "No object"
