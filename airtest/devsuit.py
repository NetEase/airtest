#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import os
import platform
import time
import threading
import json
from PIL import Image

from . import base
from . import proto
from .image import auto as imtauto
from .image import sift as imtsift
from .image import template as imttemplate

import airtest

log = base.getLogger('devsuit')

class DeviceSuit(object):
    def __init__(self, device, devClass, phoneno, 
            appname=None, logfile='log/airtest.log', monitor=True):
        print 'DEVSUIT_SERIALNO:', phoneno
        self.dev = devClass(phoneno)
        self.appname = appname
        self._device = device
        self._inside_depth = 0
        self._initWidthHeight()

        # default image search extentension and 
        self._image_exts = ['.jpg', '.png']
        self._image_dirs = ['.', 'image']
        self._image_pre_search_dirs = ['image-%d_%d'%(self.width, self.height), 
                'image-'+device]
        self._image_match_method = 'auto'
        self._threshold = 0.3 # for findImage

        self._rotation = None # UP,DOWN,LEFT,RIGHT
        self._tmpdir = 'tmp'
        self._click_timeout = 20.0 # if icon not found in this time, then panic
        self._delay_after_click = 0.5 # when finished click, wait time
        self._screen_resolution = None

        self._snapshot_file = None
        self._keep_capture = False # for func:keepScreen,releaseScreen
        self._logfile = logfile
        self._loglock = threading.Lock()

        logdir = os.path.dirname(logfile) or '.'
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        if os.path.exists(logfile):
            backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
            os.rename(logfile, backfile)

        #-- start of func setting
        self._init_monitor()
        if monitor:
            self.monitor.start()
        def _setinterval(x):
            self.monitor._cycle = x
        self._monitor_interval = _setinterval

        # Only for android phone method=<adb|screencap>
        def _snapshot_method(method):
            if method and self._device == 'android':
                self.dev._snapshot_method = method
        self._snapshot_method = _snapshot_method
        #-- end of func setting

    def __getattribute__(self, name):
        # print name
        v = object.__getattribute__(self, name)
        if isinstance(v, collections.Callable):
            objdict = object.__getattribute__(self, '__dict__')
            # print objdict
            def _wrapper(*args, **kwargs):
                objdict['_inside_depth'] += 1
                # log function call
                ret = v(*args, **kwargs)
                if objdict['_inside_depth'] == 1 and not v.__name__.startswith('_'):
                    self.log(proto.TAG_FUNCTION, dict(name=v.__name__, args=args, kwargs=kwargs))
                objdict['_inside_depth'] -= 1
                return ret
            return _wrapper
        return v

    def _init_monitor(self):
        def _cpu_mem_monitor():
            if not self.appname:
                return
            meminfo = self.dev.meminfo(self.appname)
            self.log(proto.TAG_MEMORY, meminfo)
            cpuinfo = self.dev.cpuinfo(self.appname)
            self.log(proto.TAG_CPU, cpuinfo)

        self.monitor = airtest.monitor.Monitor()
        self.monitor.addfunc(_cpu_mem_monitor)
        self.monitor._cycle = 5.0 # the default value

    def _imfind(self, bgimg, search):
        method = self._image_match_method
        if method == 'auto':
            point = imtauto.locate_one_image(bgimg, search, threshold=self._threshold)
        elif method == 'template':
            point = imttemplate.find(search, bgimg, self._threshold)
        elif method == 'sift':
            point = imtsift.find(search, bgimg)
        else:
            raise RuntimeError("Unknown image match method: %s" %(method))
        print 'find method=', method
        return point

    def _imfindall(self, bgimg, search, maxcnt, sort):
        if not maxcnt:
            maxcnt = 0
        method = self._image_match_method
        if method == 'auto':
            points = imtauto.locate_more_image_Template(search, bgimg, num=maxcnt)
        elif method == 'template':
            points = imttemplate.findall(search, bgimg, self._threshold, maxcnt=maxcnt)
        elif method == 'sift':
            points = imtsift.findall(search, bgimg, maxcnt=maxcnt)
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
        raise RuntimeError('Image file(%s) not found in %s' %(filename, self._image_pre_search_dirs+self._image_dirs))

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
        # use last snapshot file
        if self._snapshot_file and self._keep_capture:
            return self._snapshot_file

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
            angle = dict(RIGHT=Image.ROTATE_90, LEFT=Image.ROTATE_270).get(rotation)
            Image.open(filename).transpose(angle).save(filename)
        if tempdir:
            self.log(proto.TAG_SNAPSHOT, dict(filename=filename))
        self._snapshot_file = filename
        return filename

    def log(self, tag, message):
        self._loglock.acquire()
        timestamp = time.time()
        try:
            dirname = os.path.dirname(self._logfile) or '.'
            if not os.path.exists(dirname):
                os.path.makedirs(dirname)
        except:
            pass
        with open(self._logfile, 'a') as file:
            data = dict(timestamp=int(timestamp), tag=tag, data=message)
            file.write(json.dumps(data) + '\n')
        self._loglock.release()

    def keepCapture(self):
        '''
        Use screen in memory
        '''
        self._keep_capture = True

    def releaseCapture(self):
        '''
        Donot use screen in memory (this is default behavior)
        '''
        self._keep_capture = False

    def takeSnapshot(self, filename):
        '''
        Take screen snapshot

        @param filename: string (base filename want to save as basename)
        @return string: (filename that really save to)
        '''
        savefile = self._saveScreen(filename, random_name=False, tempdir=False)
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
            key = '_'+k
            if hasattr(self, key):
                item = getattr(self, key)
                if callable(item):
                    item(v)
                else:
                    setattr(self, key, v)
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
        if self._screen_resolution:
            # resize image
            w, h = self._screen_resolution
            (ratew, rateh) = self.width/float(w), self.height/float(h)
            im = Image.open(filepath)
            (rw, rh) = im.size
            new_name = base.random_name('resize-{t}-XXXX.png'.format(t=time.strftime("%y%m%d%H%M%S")))
            new_name = os.path.join(self._tmpdir, new_name)
            im.resize((int(ratew*rw), int(rateh*rh))).save(new_name)
            filepath = new_name
        pt = self._imfind(screen, filepath)
        return pt

    def mustFind(self, imgfile):
        ''' 
        Raise Error if image not found
        '''
        pt = self.find(imgfile)
        if not pt:
            raise RuntimeError("Image[%s] not found" %(imgfile))
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

    def safeWait(self, imgfile, seconds):
        '''
        Like wait, but don't raise RuntimeError

        return None when timeout
        return point if found
        '''
        try:
            return self.wait(imgfile, seconds)
        except:
            return None

    def wait(self, imgfile, seconds=20):
        '''
        Wait until some picture exists
        @return position when imgfile shows
        @raise RuntimeError if not found
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

    def click(self, SF, seconds=None, duration=0.1):
        '''
        Click function
        @param seconds: float (if time not exceed, it will retry and retry)
        '''
        if seconds == None:
            seconds = self._click_timeout
        log.info('CLICK %s, timeout=%.2fs, duration=%.2fs', SF, seconds, duration)
        point = self._PS2Point(SF)
        if point:
            (x, y) = point
        else:
            (x, y) = self.wait(SF, seconds=seconds)
            log.info('Click %s point: (%d, %d)', SF, x, y)
        self.dev.touch(x, y, duration)
        log.debug('delay after click: %.2fs' ,self._delay_after_click)

        # FIXME(ssx): mark point(not tested) alse need globalSet
        # import cv2
        # import aircv as ac
        # if os.path.exists(self._snapshot_file):
        #     img = ac.imread(self._snapshot_file)
        #     ac.mark_point(img, (x, y))
        #     cv2.imwrite(self._snapshot_file, img)

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

    def drag(self, fpt, tpt, duration=0.5):
        ''' 
        Drag from one place to another place

        @param fpt,tpt: filename or position
        @param duration: float (duration of the event in seconds)
        '''
        fpt = self._PS2Point(fpt)
        tpt = self._PS2Point(tpt)
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


