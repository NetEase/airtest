#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from airtest import image
from airtest import base
from airtest import jsonlog
from airtest import device
from airtest import patch

log = base.getLogger('devsuit')

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

def find_multi_image(orig, query, threshold):
    return [find_one_image(orig, query, threshold)]
    
def find_one_image(orig, query, threshold):
    pts = image.locate_image(orig, query, threshold=threshold)
    if len(pts) > 1:
        raise RuntimeError('too many same query images')
    if len(pts) == 0:
        raise RuntimeError('query image not found')
    return pts[0]

def get_jsonlog(filename='log/airtest.log'):    
    logfile = os.getenv('AIRTEST_LOGFILE', filename)
    if os.path.exists(logfile):
        backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
        os.rename(logfile, backfile)
    else:
        base.makedirs(base.dirname(logfile))
    jlog = jsonlog.JSONLog(logfile)
    return jlog

class DeviceSuit(object):
    def __init__(self, device, serialno, appname=None):
        self.dev = device(serialno)
        self.appname = appname

        w, h = self.dev.shape()
        self.width = min(w, h)
        self.height = max(w, h)

        self._threshold = 0.3 # for findImage
        self._rotation = None # UP,DOWN,LEFT,RIGHT
        self._log = get_jsonlog().writeline # should implementes writeline(dict)
        self._tmpdir = 'tmp'

        @patch.go
        def _monitor(interval=3):
            log.debug('MONITOR started')
            if not self.appname:
                log.debug('MONITOR finished, no package provided')
                return
            while True:
                start = time.time()
                mem = self.dev.getMem(self.appname)
                self._log({'type':'record', 'mem':mem})
                cpu = self.dev.getCpu(self.appname)
                self._log({'type':'record', 'cpu':cpu})
                dur = time.time()-start
                if interval > dur:
                    time.sleep(interval-dur)
        _monitor()

    def _fixPoint(self, (x, y)):
        width, height = self.width, self.height
        if isinstance(x, float) and x <= 1.0:
            x = int(width*x)
        if isinstance(y, float) and y <= 1.0:
            y = int(width*y)
        rotation = self._rotation
        if not rotation:
            (w, h) = self.dev.shape() # when rotate w > h
            if w != width:
                rotation = 'RIGHT'
            else:
                rotation = 'UP'
        nx, ny = rotate_point((x, y), (width, height), rotation)
        if rotation != 'UP':
            log.debug('Screen rotate direction(%s), width(%d), height(%d)', rotation, w, h)
            log.debug('(%d, %d) -> (%d, %d)', x, y, nx, ny)
        return (nx, ny)

    def _PS2Point(self, PS):
        if isinstance(PS, basestring):
            log.debug('locate postion to touch')
            PS = self.find(PS)
        (x, y) = self._fixPoint(PS)#(PS[0], PS[1]))#(1L, 2L))
        return (x, y)

    def _saveScreen(self, filename):
        if not os.path.exists(self._tmpdir):
            base.makedirs(self._tmpdir)

        filename = os.path.join(self._tmpdir, base.random_name(filename))
        self.dev.snapshot(filename)
        self._log(dict(action='snapshot', filename=filename))
        return filename

    def takeSnapshot(self, filename):
        '''
        Take screen snapshot

        @param filename: string (base filename want to save as basename)
        @return string: (filename that really save to)
        '''
        savefile = self._saveScreen(filename)
        self._log(dict(type='snapshot', filename=savefile))

    def globalSet(self, m={}):
        '''
        app setting, be careful you should known what you are doing.
        @parma m(dict): eg:{"threshold": 0.3}
        '''
        for k,v in m.items():
            if hasattr(self, '_'+k):
                setattr(self, '_'+k, v)
            else:
                print 'not have such setting: %s' %(k)

    def find(self, imgfile):
        '''
        Find image position on screen

        @return (point that found)
        '''
        if not os.path.exists(imgfile):
            raise RuntimeError('image file(%s) not exists' %(imgfile))
        screen = self._saveScreen('screen-{t}-XXXX.png'.format(t=time.strftime("%y%m%d%H%M%S")))
        pt = find_one_image(screen, imgfile, self._threshold)
        return pt

    def findAll(self, imgfile):
        '''
        Find multi positions that imgfile on screen
        @return list point that found
        @warn not finished yet.
        '''
        screen = self._saveScreen('find-XXXXXXXX.png')
        pts = find_multi_image(screen, imgfile, self._threshold)
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

    def click(self, SF):
        x, y = self._PS2Point(SF)
        log.info('click %s point: (%d, %d)', SF, x, y)
        self.dev.touch(x, y)

    def clickOnAppear(self, imgfile, seconds=20):
        '''
        When imgfile exists, then click it
        '''
        log.info('click image file: %s', imgfile)
        p = self.wait(imgfile, seconds)
        return self.click(p)

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
                    variable['screen'] = self._saveScreen('drag-XXXXXXXX.png')
                pt = find_one_image(variable['screen'], raw, self._threshold)
                return self._fixPoint(pt)
            raise RuntimeError('unknown type')

        fpt, tpt = to_point(fpt), to_point(tpt)
        return self.dev.drag(fpt, tpt, duration)

    def sleep(self, secs=1.0):
        '''
        Sleeps for the specified number of seconds

        @param secs: float (number of seconds)
        @return None
        '''
        log.debug('SLEEP %.2fs', secs)
        time.sleep(secs)

    def type(self, text):
        '''
        Input some text

        @param text: string (text want to type)
        '''
        self.dev.type(text)

    def shape(self):
        '''
        Get device shape

        @return (width, height)
        '''
        return self.dev.shape()

    def keyevent(self, event):
        '''
        Send keyevent (only support android and ios)

        @param event: string (one of MENU,BACK,HOME)
        @return nothing
        '''
        if hasattr(self.dev, 'keyevent'):
            return self.dev.keyevent(event)
        raise RuntimeError('keyevent not support')

#if __name__ == '__main__':
#    serialno = '10.242.62.143:5555'
#    deviceType = 'android'
#
#    dev = connect(serialno, device=deviceType)
#    dev.click('hello.png')
