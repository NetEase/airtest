#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import time
import json
import PIL

from airtest import base
from airtest import jsonlog
from airtest import patch

from airtest import image as imt
# from airtest.image import auto as image

import airtest

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
    def __init__(self, device, devClass, phoneno, 
            appname=None, logfile='log/airtest.log', monitor=True):
        print 'DEVSUIT_SERIALNO:', phoneno
        self.dev = devClass(phoneno)
        self.appname = appname
        self._device = device

        self._initWidthHeight()

        # default image search extentension and 
        self._image_exts = ['.jpg', '.png']
        self._image_dirs = ['.', 'image']
        self._image_pre_search_dirs = ['image-%d_%d'%(self.width, self.height), 
                'image-'+device]
        self._image_match_method = 'auto'
        self._threshold = 0.3 # for findImage

        self._rotation = None # UP,DOWN,LEFT,RIGHT
        self._log = get_jsonlog(logfile).writeline # should implementes writeline(dict)
        self._tmpdir = 'tmp'
        self._log(dict(type='start', timestamp=time.time()))
        self._configfile = os.getenv('AIRTEST_CONFIG') or 'air.json'
        self._enable_monitor = True
        self._monitor_interval = 5
        self._click_timeout = 20.0 # if icon not found in this time, then panic
        self._delay_after_click = 0.5 # when finished click, wait time

        self._snapshot_file = None
        self._quit = False

        @patch.go
        def _monitor():
            log.debug('MONITOR started')
            if not self.appname:
                log.debug('MONITOR finished, no appname provided')
                return
            while True and self._enable_monitor and not self._quit:
                start = time.time()
                mem = self.dev.getMem(self.appname)
                self._log({'type':'record', 'mem':mem.get('PSS', 0)/1024})
                self._log({'type':'record', 'mem_details':mem})
                cpu = self.dev.getCpu(self.appname)
                self._log({'type':'record', 'cpu':cpu})
                dur = time.time()-start
                if self._monitor_interval > dur:
                    time.sleep(self._monitor_interval-dur)
        if monitor:
            _monitor()

    def _imfind(self, bgimg, search):
        method = self._image_match_method
        if method == 'auto':
            point = imt.auto.locate_one_image(bgimg, search, threshold=self._threshold)
        elif method == 'template':
            point = imt.template.find(search, bgimg, self._threshold)
        else:
            raise RuntimeError("Unknown image match method: %s" %(method))
        print 'find method=', method
        return point

    def _imfindall(self, bgimg, search, maxcnt, sort):
        method = self._image_match_method
        if method == 'auto':
            if not maxcnt:
                maxcnt = 0
            points = imt.auto.locate_more_image_Template(search, bgimg, num=maxcnt)
        elif method == 'template':
            points = imt.template.findall(search, bgimg, self._threshold, maxcnt=maxcnt)
        else:
            raise RuntimeError("Unknown image match method: %s" %(method))
        if sort:
            def cmpy((x0, y0), (x1, y1)):
                return y1<y0
            def cmpx((x0, y0), (x1, y1)):
                return x1<x1
            m = {'x': cmpx, 'y': cmpy}
            points.sort(cmp=m[sort])
        return points

    def _initWidthHeight(self):
        w, h = self.dev.shape()
        if self._device != 'windows':
            self.width = min(w, h)
            self.height = max(w, h)
        else:
            self.width = w
            self.height = h

    def _getRotation(self):
        '''
        @return UP|RIGHT|DOWN|LEFT
        '''
        if self._device == 'windows':
            return 'UP'
        rotation = self._rotation
        if not rotation:
            (w, h) = self.dev.shape() # when rotate w > h
            if w != self.width:
                rotation = 'RIGHT'
            else:
                rotation = 'UP'
        return rotation

    def _fixPoint(self, (x, y)):
        width, height = self.width, self.height
        rotation = self._getRotation()
        if rotation in ('RIGHT', 'LEFT'):
            width, height = max(height,width), min(height,width) # adjust width > height
        if isinstance(x, float) and x <= 1.0:
            x = int(width*x)
        if isinstance(y, float) and y <= 1.0:
            y = int(height*y)
        return (x, y)

    def _search_image(self, filename):
        ''' Search image in default path '''
        if isinstance(filename, unicode) and platform.system() == 'Windows':
            filename = filename.encode('gbk')
            #filename = filename.encode('utf-8')
        basename, ext = os.path.splitext(filename)
        exts = [ext] if ext else self._image_exts
        for folder in self._image_pre_search_dirs + self._image_dirs:
            for ext in exts:
                fullpath = os.path.join(folder, basename+ext)
                if os.path.exists(fullpath):
                    return fullpath
        raise RuntimeError('Image file(%s) not found in %s' %(filename, self._image_dirs))

    def _PS2Point(self, PS):
        '''
        Convert PS to point
        @return (x, y) or None if not found
        '''
        if isinstance(PS, basestring):
            PS = self.find(PS)
            if not PS:
                return None
        (x, y) = self._fixPoint(PS)#(PS[0], PS[1]))#(1L, 2L))
        return (x, y)

    def _saveScreen(self, filename, random_name=True, tempdir=True):
        if random_name:
            filename = base.random_name(filename)
        if tempdir:
            filename = os.path.join(self._tmpdir, filename)

        parent_dir = os.path.dirname(filename) or '.'
        if not os.path.exists(parent_dir):
            base.makedirs(parent_dir)

        self.dev.snapshot(filename)

        if self._device == 'windows':
            return filename
        rotation = self._getRotation()
        # the origin screenshot is UP, so need to rotate it here for human
        if rotation != 'UP':
            angle = dict(RIGHT=PIL.Image.ROTATE_90, LEFT=PIL.Image.ROTATE_270).get(rotation)
            PIL.Image.open(filename).transpose(angle).save(filename)
        self._log(dict(type='snapshot', filename=filename))
        self._snapshot_file = filename
        return filename

    def takeSnapshot(self, filename):
        '''
        Take screen snapshot

        @param filename: string (base filename want to save as basename)
        @return string: (filename that really save to)
        '''
        savefile = self._saveScreen(filename, random_name=False, tempdir=False)
        self._log(dict(type='snapshot', filename=savefile))
        return savefile

    def globalSet(self, *args, **kwargs):
        '''
        app setting, be careful you should known what you are doing.
        @parma m(dict): eg:{"threshold": 0.3}
        '''
        if len(args) > 0:
            m = args[0]
            assert isinstance(m, dict)
        else:
            m = kwargs
        for k,v in m.items():
            if hasattr(self, '_'+k):
                setattr(self, '_'+k, v)
            else:
                print 'not have such setting: %s' %(k)

    def globalGet(self, key):
        '''
        get app setting
        '''
        if hasattr(self, '_'+key):
            return getattr(self, '_'+key)
        return None

    def find(self, imgfile):
        '''
        Find image position on screen

        @return (point founded or None if not found)
        '''
        filepath = self._search_image(imgfile)
        log.debug('Locate image path: %s', filepath)
        screen = self._saveScreen('screen-{t}-XXXX.png'.format(t=time.strftime("%y%m%d%H%M%S")))
        pt = self._imfind(screen, filepath)
        # pt = find_one_image(screen, filepath, self._threshold)
        return pt

    def findall(self, imgfile, maxcnt=None, sort=None):
        '''
        Find multi positions that imgfile on screen

        @maxcnt (int): max number of object restricted.
        @sort (string): (None|x|y) x to sort with x, small in front, None to be origin order
        @return list point that found
        @warn not finished yet.
        '''
        filepath = self._search_image(imgfile)
        screen = self._saveScreen('find-XXXXXXXX.png')
        pts = self._imfindall(screen, filepath, maxcnt, sort)
        return pts

    def wait(self, imgfile, seconds=20):
        '''
        Wait until some picture exists
        @return position when imgfile shows
        '''
        log.info('WAIT: %s', imgfile)
        start = time.time()
        while True:
            pt = self.find(imgfile)
            if pt:
                return pt
            if time.time()-start > seconds:
                break
            time.sleep(1)
        raise RuntimeError('Wait timeout(%.2f)', float(seconds))

    def exists(self, imgfile):
        return True if self.find(imgfile) else False

    def click(self, SF, seconds=None, eventType=airtest.EV_DOWN_AND_UP):
        '''
        Click function
        @param seconds: float (if time not exceed, it will retry and retry)
        '''
        if seconds == None:
            seconds = self._click_timeout
        log.info('CLICK %s, timeout=%.2f', SF, seconds)
        point = self._PS2Point(SF)
        if point:
            (x, y) = point
            self.dev.touch(x, y, eventType)
        else:
            (x, y) = self.wait(SF, seconds=seconds)
            log.info('Click %s point: (%d, %d)', SF, x, y)
            self.dev.touch(x, y, eventType)
        log.debug('delay after click: %.2fs' ,self._delay_after_click)

        # mark position
        import cv2
        img = cv2.imread(self._snapshot_file)
        if img != None:
            img = imt.toolbox.markPoint(img, (x, y))
            cv2.imwrite(self._snapshot_file, img)

        time.sleep(self._delay_after_click)

    def center(self):
        '''
        Center position
        '''
        w, h = self.shape()
        return w/2, h/2
    
    def clickIfExists(self, imgfile):
        '''
        Click when image file exists

        @return (True|False) if clicked
        '''
        log.info('CLICK IF EXISTS: %s' %(imgfile))
        pt = self.find(imgfile)
        if pt:
            log.debug('click for exists %s', imgfile)
            self.click(pt)
            return True
        else:
            log.debug('ignore for no exists %s', imgfile)
            return False

    def drag(self, fpt, tpt, duration=500):
        ''' 
        Drag from one place to another place

        @param fpt,tpt: filename or position
        @param duration: float (duration of the event in ms)
        '''
        # the duration seems not working. no matter how larger I set, nothing changes.
        # variable = {}
        # def to_point(raw):
        #     if isinstance(raw, list) or isinstance(raw, tuple):
        #         return self._fixPoint(raw)
        #     if isinstance(raw, basestring):
        #         screen = variable.get('screen')
        #         if not screen:
        #             variable['screen'] = self._saveScreen('drag-XXXXXXXX.png')
        #         pt = find_one_image(variable['screen'], raw, self._threshold)
        #         return self._fixPoint(pt)
        #     raise RuntimeError('unknown type')
        # FIXME: (a little slow, find should support specified images)
        fpt = self.find(fpt)
        tpt = self.find(tpt)
        # fpt, tpt = to_point(fpt), to_point(tpt)
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

    def close(self):
        '''
        Release resouces
        '''
        self._quit = True
        time.sleep(0.5)

    def _safe_load_config(self):
        import os
        if os.path.exists(self._configfile):
            return json.load(open(self._configfile))
        return {}
            
    def start(self):
        '''
        Start a app
        '''
        s = self._safe_load_config()
        ret = self.dev.start(self.appname, s.get(self._device))
        self._initWidthHeight()
        return ret
    
    def stop(self):
        '''
        Stop a app
        '''
        s = self._safe_load_config()
        return self.dev.stop(self.appname, s.get(self._device))

    def clear(self):
        '''
        Stop app and clear data
        '''
        s = self._safe_load_config()
        return self.dev.clear(self.appname, s.get(self._device))

