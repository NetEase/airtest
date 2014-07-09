#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import time

from airtest import image
from airtest import patch
from airtest import base
from airtest import jsonlog

from com.dtmilano.android.viewclient import ViewClient 
from com.dtmilano.android.viewclient import adbclient

DEBUG = os.getenv("DEBUG")=="true"
 
log = base.getLogger('android')

def getMem(serialno, package):
    '''
    @param package(string): android package name
    @return float: the memory, unit MB
    '''
    command = 'adb -s %s shell dumpsys meminfo' % serialno
    mem_info = base.check_output(command).splitlines()
    try:
        xym_mem = filter(lambda x: package in x, mem_info)[0].split()[0]
        mem = float(xym_mem) / 1024
        log.info("mem_info:%s" % mem)
        return mem
    except IndexError:
        log.error("mem_info error")
        return 0

def getCpu(serialno, package):
    '''
    @param package(string): android package name
    @return float: the cpu usage
    '''
    command = 'adb -s %s shell dumpsys cpuinfo' % serialno
    cpu_info = base.check_output(command).splitlines()
    try:
        xym_cpu = filter(lambda x: package in x, cpu_info)[0].split()[0]
        cpu = float(xym_cpu[:-1])
        log.info("cpu_info:%s" % cpu)
        return cpu
    except IndexError:
        log.error("cpu_info error")
        return 0

def find_image(orig, query, threshold):
    pts = _image_locate(orig, query, threshold)
    if len(pts) > 1:
        raise RuntimeError('too many same query images')
    if len(pts) == 0:
        raise RuntimeError('query image not found')
    return pts[0]

def rotate_point((x, y), (w, h), d):
    '''
    @param (x,y): input point
    @param (w,h): width and height
    @param d(string): one of UP,DOWN,LEFT,RIGHT
    @return (x, y): rotated point
    '''
    if d == 'UP':
        return x, y
    if d == 'DOWN':
        return w-x, y-y
    if d == 'RIGHT':
        return y, w-x
    if d == 'LEFT':
        return h-y, x

# prepare log and tmp dir
logfile = os.getenv('AIRTEST_LOGFILE', 'log/airtest.log')
if os.path.exists(logfile):
    backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
    os.rename(logfile, backfile)
else:
    base.makedirs(base.dirname(logfile))
jlog = jsonlog.JSONLog(logfile)

@patch.record(jlog)
class AndroidDevice(object):
    def __init__(self, serialno=None, pkgname=None):
        self._last_point = None
        self._threshold = 0.3 # for findImage
        self._rotation = None # UP,DOWN,LEFT,RIGHT
        self._tmpdir = 'tmp'

        if not os.path.exists(self._tmpdir):
            base.makedirs(self._tmpdir)

        self.pkgname = pkgname
        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.reconnect = True # this way is more stable

        w = self.adb.getProperty("display.width")
        h = self.adb.getProperty("display.height")
        self._width = min(w, h)
        self._height = max(w, h)

        self.vc = ViewClient(self.adb, serialno)
        ViewClient.connectToDeviceOrExit()
        brand = self.adb.getProperty('ro.product.brand')
        serialno = self.adb.getProperty('ro.boot.serialno')
        log.debug('wake phone: brand:{brand}, serialno:{serialno}'.format(
            brand=brand, serialno=self._serialno))
        try:
            self.adb.wake()
            if not self.adb.isScreenOn():
                time.sleep(1)
            log.debug('isScreenOn: %s', self.adb.isScreenOn())
            if self.adb.isLocked():
                (w, h) = self._getShape()
                self.drag((w*0.2, h*0.5), (w*0.6, h*0.5))
        except:
            print 'Device not support screen detect'

        @base.go
        def monitor(interval=3):
            log.debug('MONITOR started')
            if not self.pkgname:
                log.debug('MONITOR finished, no package provided')
                return
            while True:
                start = time.time()
                mem = self._getMem()
                jlog.writeline({'type':'record', 'mem':mem})
                cpu = self._getCpu()
                jlog.writeline({'type':'record', 'cpu':cpu})
                dur = time.time()-start
                if interval > dur:
                    print 'MEM:', mem
                    print 'CPU:', cpu
                    time.sleep(interval-dur)
        monitor()

    def _fixPoint(self, (x, y)):
        width, height = self._width, self._height
        if isinstance(x, float) and x <= 1.0:
            x = int(width*x)
        if isinstance(y, float) and y <= 1.0:
            y = int(width*y)
        rotation = self._rotation
        if not rotation:
            (w, h) = self._getShape() # when rotate w > h
            if w != width:
                rotation = 'RIGHT'
            else:
                rotation = 'UP'
        nx, ny = rotate_point((x, y), (width, height), rotation)
        if rotation != 'UP':
            log.debug('Screen rotate direction(%s), width(%d), height(%d)', rotation, w, h)
            log.debug('(%d, %d) -> (%d, %d)', x, y, nx, ny)
        return (nx, ny)

    def _getShape(self):
        width = self.adb.getProperty("display.width")
        height = self.adb.getProperty("display.height")
        return (width, height)
    
    def _saveScreen(self, filename):
        filename = os.path.join(self._tmpdir, base.random_name(filename))
        self.takeSnapshot(filename)
        return filename

    def globalSet(self, m={}):
        '''
        app setting, be careful you should known what you are doing.
        @parma m(dict): eg:{"threshold": 0.3}
        '''
        keys = ['threshold']
        for k,v in m.items():
            if hasattr(self, '_'+k):
                setattr(self, '_'+k, v)
            else:
                print 'not have such setting: %s' %(k)

    def setThreshold(self, threshold):
        '''
        @param threshold(float): (0, 1] suggest 0.5
        '''
        self.globalSet({'threshold': threshold})

    def takeSnapshot(self, filename):
        ''' save screen snapshot '''
        jlog.writeline({'type':'snapshot', 'filename':filename})
        log.debug('take snapshot and save to '+filename)
        pil = self.adb.takeSnapshot(reconnect=True)
        pil.save(filename)

    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        '''
        same as adb -s ${SERIALNO} shell input tap x y
        '''
        log.debug('touch position %s', (x, y))
        self.adb.touch(x, y, eventType)

    def shape(self):
        ''' 
        Get screen width and height 
        '''
        return self._getShape()

    def find(self, imgfile):
        '''
        Find image position on screen

        @return (point that found)
        '''
        screen = self._saveScreen('screen-{t}-XXXX.png'.format(t=time.strftime("%y%m%d%H%M%S")))
        if not os.path.exists(imgfile):
            raise RuntimeError('image file(%s) not exists' %(imgfile))
        pts = _image_locate(screen, imgfile, self._threshold)
        return pts and pts[0]

    def findAll(self, imgfile):
        '''
        Find multi positions that imgfile on screen
        @return list point that found
        @warn not finished yet.
        '''
        screen = self._saveScreen('find-XXXXXXXX.png')
        pts = _image_locate(screen, imgfile, self._threshold)
        return pts

    def wait(self, imgfile, seconds=20):
        '''
        Wait until some picture exists
        @return position when imgfile shows
        '''
        interval = 1
        max_retry = int(seconds/interval)
        pt = base.wait_until(self.find, args=(imgfile,), interval=interval, max_retry=max_retry)
        if not pt:
            raise RuntimeError('wait fails')
        self._last_point = pt
        return pt

    def exists(self, imgfile):
        return True if self.find(imgfile) else False

    def click(self, pt):
        '''
        Click

        @param pt: string or list(x, y) (point to click, when string is image file)
        '''
        if isinstance(pt, basestring):
            log.debug('locate postion to touch')
            pt = self.find(pt)
        (x, y) = self._fixPoint(pt)
        print 'click', (x, y)
        self.adb.touch(x, y)

    def clickOnAppear(self, imgfile, seconds=20):
        '''
        When imgfile exists, then click it
        '''
        p = self.wait(imgfile, seconds)
        return self.click(p)

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
            raise RuntimeError('text(%s) not found' % text)

    def drag(self, fpt, tpt, duration=500):
        ''' 
        Drag from one place to another place

        @param fpt,tpt: filename or position
        @param duration: float (duration of the event in ms)
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
                pt = find_image(variable['screen'], raw, self._threshold)
                return self._fixPoint(pt)
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
        '''
        Input some text

        @param text: string (text want to type)
        '''
        log.debug('type text: %s', repr(text))
        keymap = {
                '\n': 'ENTER',
                ' ': 'SPACE',
                '\t': 'TAB',
                }
        for c in text:
            if c in keymap:
                self.adb.press(keymap[c])
            else:
                self.adb.type(c)

    def _getMem(self):
        return getMem(self._serialno, self.pkgname)

    def _getCpu(self):
        return getCpu(self._serialno, self.pkgname)

def _image_locate(origin_file, query_file, threshold=0.3):
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
