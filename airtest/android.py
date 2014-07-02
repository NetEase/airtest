#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import time
import requests
import json
import logging
import random
import string

from airtest import image, patch, base

from com.dtmilano.android.viewclient import ViewClient 
from com.dtmilano.android.viewclient import adbclient

DEBUG = os.getenv("DEBUG")=="true"

logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level = logging.DEBUG)  
log = logging.getLogger('root')
random.seed(time.time())

def _wait_until(until_func, interval=0.5, max_retry=10, args=(), kwargs={}):
    '''
    @return True(when found), False(when not found)
    '''
    log.debug('wait func: %s', until_func.__name__)
    retry = 0
    while retry < max_retry:
        retry += 1
        ret = until_func(*args, **kwargs)
        if ret:
            return ret
        log.debug('wait until: %s, sleep: %s', until_func.__name__, interval)
        time.sleep(interval)
    return None

def _random_name(name):
    out = []
    for c in name:
        if c == 'X':
            c = random.choice(string.ascii_lowercase)
        out.append(c)
    return ''.join(out)

@patch.record()
class AndroidDevice(object):
    def __init__(self, serialno=None):
        self._imgdir = None
        self._last_point = None
        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.reconnect = True # this way is more stable

        self.vc = ViewClient(self.adb, serialno)
        ViewClient.connectToDeviceOrExit()
        brand = self.adb.getProperty('ro.product.brand')
        serialno = self.adb.getProperty('ro.boot.serialno')
        log.debug('wake phone: brand:{brand}, serialno:{serialno}'.format(
            brand=brand, serialno=serialno))
        try:
            self.adb.wake()
            if not self.adb.isScreenOn():
                time.sleep(1)
            log.debug('isScreenOn: %s', self.adb.isScreenOn())
            if self.adb.isLocked():
                (w, h) = self._getShape()
                app.drag((w*0.2, h*0.5), (w*0.6, h*0.5))
        except:
            print 'Device not support screen detect'

    def _fixPoint(self, (x, y)):
        (w, h) = self._getShape() # when rotate w > h
        width, height = min(w, h), max(w, h)
        if isinstance(x, float) and x <= 1.0:
            x = int(width*x)
        if isinstance(y, float) and y <= 1.0:
            y = int(width*y)
        if w != width:
            log.debug('Screen rotate, width(%d), height(%d)', w, h)
            log.debug('(%d, %d) -> (%d, %d)', x, y, y, h-x)
            x, y = y, width-x
        return (x, y)


        pass
    def _imgfor(self, name):
        if self._imgdir:
            return os.path.join(self._imgdir, name)
        return name

    def _getShape(self):
        width = self.adb.getProperty("display.width")
        height = self.adb.getProperty("display.height")
        return (width, height)
    
    def shape(self):
        ''' get screen width and height '''
        return self._getShape()

    def setThreshold(self, threshold):
        '''
        @param threshold(float): (0, 1] suggest 0.5
        '''
        self._threshold = threshold

    def setImageDir(self, imgdir='.'):
        self._imgdir = imgdir

    def _saveScreen(self, filename):
        filename = _random_name(filename)
        self.takeSnapshot(filename)
        return filename

    def takeSnapshot(self, filename=None):
        ''' @return PIL image '''
        log.debug('take snapshot and save to '+filename)
        pil = self.adb.takeSnapshot(reconnect=True)
        if filename:
            pil.save(filename)
        return pil

    def startActivity(self, appname):
        return self.adb.startActivity(appname)

    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        log.debug('touch position %s', (x, y))
        self.adb.touch(x, y, eventType)
        #base.exec_cmd('adb', '-s', self._serialno, 
                #'shell', 'input', 'tap', '%d'%x, '%d'%y)

    def wait(self, imgfile, interval=0.5, max_retry=5):
        '''
        wait until some picture exists
        '''
        pt = _wait_until(self.find, args=(imgfile,), interval=interval, max_retry=max_retry)
        if not pt:
            raise Exception('wait fails')
        self._last_point = pt
        return

    def find(self, imgfile):
        '''
        find image location
        @return list of find points
        '''
        screen = self._saveScreen('find-XXXXXXXX.png')
        pts = _image_locate(screen, self._imgfor(imgfile), self._threshold)
        return pts and pts[0]

    def exists(self, imgfile):
        return True if self.find(imgfile) else False

    def click(self, pt):
        '''
        @param pt(string or list(x, y)): point to click, when string is image file
        '''
        if isinstance(pt, basestring):
            log.debug('locate postion to touch')
            pt = self.find(pt)
        (x, y) = self._fixPoint(pt)
        print 'click', imgfile, (x, y)
        self.adb.touch(x, y)
        # check if horizontal
        # w, h = self._getShape()
        # if w > h:
        #     log.debug('Screen rotate, width(%d), height(%d)', w, h)
        #     log.debug('(%d, %d) -> (%d, %d)', x, y, y, h-x)
        #     x, y = y, h-x

    def clickByText(self, text, dump=True, delay=1.0):
        self.sleep(delay)
        if dump:
            log.debug('dump icons')
            self.vc.dump()
        b = self.vc.findViewWithText(text)
        if b:
            (x, y) = b.getXY()
            log.debug('click x: %d y: %d', x, y)
            b.touch()
        else:
            raise Exception('text(%s) not found' % text)

    def drag(self, fpt, tpt, duration=500):
        ''' 
        @param fpt,tpt: (x, y) or image filepath, from point and to point
        @param duration: duration of the event in ms
        '''
        # the duration seems not working. no matter how larger I set, nothing changes.
        variable = {}
        def to_point(raw):
            if isinstance(raw, list) or isinstance(raw, tuple):
                return self._fixPoint(raw)
            if isinstance(raw, basestring):
                screen = variable.get('screen')
                if not screen:
                    variable['screen'] = self._saveScreen('screen-XXXXXXXX.png')
                pt = _image_locate_one(variable['screen'], self._imgfor(raw))
                return pt
            raise RuntimeError('unknown type')

        fpt, tpt = to_point(fpt), to_point(tpt)
        return self.adb.drag(fpt, tpt, duration)

    def sleep(self, secs=1.0):
        '''
        Sleeps for the specified number of seconds

        @param secs: float (number of seconds)
        @return None
        '''
        log.debug('SLEEP %.2fs', secs)
        time.sleep(secs)

    def keyevent(self, name):
        log.debug('keyevent touch %s', name)
        self.adb.shell('input keyevent '+name)

    def home(self):
        log.debug('touch %s', 'HOME')
        self.adb.shell('input keyevent HOME')
        
    def enter(self):
        self.adb.press('ENTER')

    def type(self, text):
        log.debug('type text: %s', repr(text))
        for c in text:
            if c == '\n':
                self.adb.press('ENTER')
            else:
                self.adb.type(c)


def _image_locate_one(orig, query):
    pts = _image_locate(orig, query)
    if len(pts) > 1:
        raise RuntimeError('too many same query images')
    if len(pts) == 0:
        raise RuntimeError('query image not found')
    return pts[0]

def _image_locate(origin_file, query_file, threshold=0.5):
    '''
    image match
    '''
    log.debug('search image(%s) from(%s)', query_file, origin_file)
    pts = image.locate_image(origin_file, query_file, threshold=threshold)
    return pts

    # when use http API, call function below
    # files={'origin': open(origin_file, 'rb'), 'query': open(query_file, 'rb')}
    # r = requests.post('http://beta.mt.nie.netease.com/api/image/locate', files=files)
    # resp = r.json()
    # if resp.get('error'):
    #     log.error('image locate: %s', resp.get('error'))
    #     raise Exception(resp.get('error'))
    # pts = r.json()['pts']
    # return pts
