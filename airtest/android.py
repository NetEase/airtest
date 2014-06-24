#!/usr/bin/env python
# coding: utf-8
#
'''
basic operation for a game(like a user does)
'''

import os
import time
import requests

import logging
from com.dtmilano.android.viewclient import ViewClient 
from com.dtmilano.android.viewclient import adbclient

DEBUG = os.getenv("DEBUG")=="true"

logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level = logging.DEBUG)  
log = logging.getLogger('root')

def _wait_until(until_func, interval=0.5, max_retry=10):
    '''
    @return True(when found), False(when not found)
    '''
    retry = 0
    while retry < max_retry:
        retry += 1
        if until_func():
            return True
        time.sleep(interval)
    return False

def hello():
    print 'hello world'
    log.debug('debue info')

class AndroidDevice(object):
    def __init__(self, serialno=None):
        self._serialno = serialno
        self._imgdir = None
        self.adb, _ = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
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

    def setImageDir(self, imgdir='.'):
        self._imgdir = imgdir

    def takeSnapshot(self, filename=None):
        ''' @return PIL image '''
        log.debug('take snapshot and save to '+filename)
        pil = self.adb.takeSnapshot(reconnect=True)
        if filename:
            pil.save(filename)
        return pil

    def startActivity(self, appname):
        return self.adb.startActivity(appname)

    def tag(self, message):
        ''' message including screenshot '''
        log.info('convery: %s', message)
        print 'message'

    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        log.debug('touch position %s', (x, y))
        self.adb.touch(x, y, eventType)

    def wait(self, timeout=None):
        log.warn('not finished')

    def click(self, imgfile, delay=0.5):
        '''
        '''
        self.takeSnapshot('screenshot.png')
        log.debug('locate postion where to touch')
        if self._imgdir:
            imgfile = os.path.join(self._imgdir, imgfile)
        pos = _image_locate('screenshot.png', imgfile)
        print 'click', imgfile, pos
        self.adb.touch(pos[0], pos[1])
        time.sleep(delay)

    def back(self):
        '''
        '''
        log.debug('touch %s', 'BACK')
        self.adb.shell('input keyevent BACK')

    def menu(self):
        log.debug('touch %s', 'MENU')
        self.adb.shell('input keyevent MENU')

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
        raise Exception(resp.get('error'))
    pts = r.json()['pts']
    if not pts:
        raise Exception("Image not match")
    return pts[0]

