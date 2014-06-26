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

# AT = ACTION
AT_KEYEVENT = 'KEYEVENT'
AT_CLICK = 'CLICK'
AT_WAIT = 'WAIT'

def _random_name(name):
    out = []
    for c in name:
        if c == 'X':
            c = random.choice(string.ascii_lowercase)
        out.append(c)
    return ''.join(out)

def record(action):
    d = {'action': action}
    def wrapper(fn):
        d.update({'func_name': fn.__name__})
        def decorator(fn, *args, **kwargs):
            print json.dumps(d)
            print type(fn), fn, args, kwargs
            fn(*args, **kwargs)
        return decorator
    return wrapper

def _record(action, images=[], **kwargs):
    d = {'action': action, 'images': images}
    d.update(kwargs)
    print json.dumps(d)

def hello():
    print 'hello world'
    log.debug('debue info')

class AndroidDevice(object):
    def __init__(self, serialno=None):
        self._imgdir = None
        self._last_point = None
        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)

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
        except:
            print 'Device not support screen detect'

    def _getShape(self):
        width = self.adb.getProperty("display.width")
        height = self.adb.getProperty("display.height")
        return (width, height)

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

    def wait(self, imgfile, interval=0.5, max_retry=5):
        '''
        wait until some picture exists
        '''
        _record(AT_WAIT)
        pts = _wait_until(self.where, args=(imgfile,), interval=interval, max_retry=max_retry)
        if not pts:
            raise Exception('wait fails')
        self._last_point = pts[0]
        return

    def where(self, imgfile):
        '''
        find image location
        @return list of find points
        '''
        screen = self._saveScreen('where-XXXXXXXX.png')
        return _image_locate(screen, imgfile)

    def exists(self, imgfile):
        return True if self.where(imgfile) else False

    #def clickIfExists(self, imgfile, delay=0.5):
    #    time.sleep(delay)
    #    pts = self.where(imgfile)
    #    if pts:
    #        p = pts[0]
    #        self.touch(*p)

    def click(self, imgfile=None, delay=1.0):
        '''
        '''
        self.sleep(delay)
        if imgfile:
            self.takeSnapshot('screenshot.png')
            log.debug('locate postion where to touch')
            if self._imgdir:
                imgfile = os.path.join(self._imgdir, imgfile)
            pos = _image_locate('screenshot.png', imgfile)[0]
        else:
            pos = self._last_point
        print 'click', imgfile, pos
        (x, y) = (pos[0], pos[1])
        w, h = self._getShape()
        # check if horizontal
        if w > h: 
            x, y = y, h-x
        _record(AT_CLICK, position=(x, y))
        self.adb.touch(x, y)

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

    def sleep(self, secs=1.0):
        '''
        Sleeps for the specified number of seconds

        @param secs: float (number of seconds)
        @return None
        '''
        log.debug('SLEEP %ds', secs)
        time.sleep(secs)

    def keyevent(self, name):
        log.debug('keyevent touch %s', name)
        self.adb.shell('input keyevent '+name)

    def home(self):
        #_record(AT_KEYEVENT, name='HOME')
        log.debug('touch %s', 'HOME')
        self.adb.shell('input keyevent HOME')
        
    def enter(self):
        self.adb.press('KEYCODE_ENTER')

    def type(self, text):
        log.debug('type text: %s', repr(text))
        for c in text:
            self.adb.type(c)
        return
        #s = []
        #for c in text:
        #    print repr(c)
        #    if c == '\n':
        #        if s:
        #            print s
        #            for char in s:
        #                self.adb.type(char)
        #            #self.adb.type(''.join(s))
        #            s = []
        #        print 'enter'
        #        self.adb.press('KEYCODE_BACK')
        #    else:
        #        s.append(c)
        #if s:
        #    self.adb.type(''.join(s))

    def drap(self, fromxy, toxy):
        print 'drap', fromxy, toxy

def _image_locate(origin_file, query_file):
    '''
    image match
    '''
    files={'origin': open(origin_file, 'rb'), 'query': open(query_file, 'rb')}
    r = requests.post('http://beta.mt.nie.netease.com/api/image/locate', files=files)
    resp = r.json()
    if resp.get('error'):
        log.error('image locate: %s', resp.get('error'))
        raise Exception(resp.get('error'))
    pts = r.json()['pts']
    return pts
