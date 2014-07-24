#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import time
import json
import PIL

from airtest import image
from airtest import base
from airtest import jsonlog
# from airtest import device
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
    if not pts:
        return None # return when nothing found
    if len(pts) > 1:
        raise RuntimeError('too many same query images')
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
    def __init__(self, device, deviceType, serialno, appname=None):
        print 'DEVSUIT_SERIALNO:', serialno
        self.dev = device(serialno)
        self.appname = appname

        w, h = self.dev.shape()
        if device != 'windows':
            self.width = min(w, h)
            self.height = max(w, h)
        else:
            self.width = w
            self.width = h

        # default image search extentension and 
        self._image_exts = ['.jpg', '.png']
        self._image_dirs = ['.', 'image']
        self._image_dirs.insert(0, 'image-'+deviceType)
        if deviceType in ('android', 'ios'):
            self._image_dirs.insert(0, 'image-%d_%d'%(self.width, self.height))

        self._threshold = 0.3 # for findImage
        self._rotation = None # UP,DOWN,LEFT,RIGHT
        self._log = get_jsonlog().writeline # should implementes writeline(dict)
        self._tmpdir = 'tmp'
        self._log(dict(type='start', timestamp=time.time()))
        self._device = deviceType
        self._configfile = os.getenv('AIRTEST_CONFIG') or 'air.json'
        self._monitor_interval = 5

        @patch.go
        def _monitor():
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
                if self._monitor_interval > dur:
                    time.sleep(self._monitor_interval-dur)
        _monitor()

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
        basename, ext = os.path.splitext(filename)
        exts = [ext] if ext else self._image_exts
        for folder in self._image_dirs:
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

    def _saveScreen(self, filename):
        if not os.path.exists(self._tmpdir):
            base.makedirs(self._tmpdir)

        filename = os.path.join(self._tmpdir, base.random_name(filename))
        self.dev.snapshot(filename)
        if self._device == 'windows':
            return filename
        rotation = self._getRotation()
        # the origin screenshot is UP, so need to rotate it here for human
        if rotation != 'UP':
            angle = dict(RIGHT=PIL.Image.ROTATE_90, LEFT=PIL.Image.ROTATE_270).get(rotation)
            PIL.Image.open(filename).transpose(angle).save(filename)
        self._log(dict(type='snapshot', filename=filename))
        return filename

    def takeSnapshot(self, filename):
        '''
        Take screen snapshot

        @param filename: string (base filename want to save as basename)
        @return string: (filename that really save to)
        '''
        savefile = self._saveScreen(filename)
        self._log(dict(type='snapshot', filename=savefile))
        return savefile

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

        @return (point founded or None if not found)
        '''
        filepath = self._search_image(imgfile)
        log.debug('Locate image path: %s', filepath)
        screen = self._saveScreen('screen-{t}-XXXX.png'.format(t=time.strftime("%y%m%d%H%M%S")))
        pt = find_one_image(screen, filepath, self._threshold)
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

    def click(self, SF, seconds=20.0):
        '''
        Click function
        @param seconds: float (if time not exceed, it will retry and retry)
        '''
        log.info('CLICK %s', SF)
        point = self._PS2Point(SF)
        if point:
            (x, y) = point
            self.dev.touch(x, y)
            return
        (x, y) = self.wait(SF, seconds=seconds)
        # while True:
        #     point = self._PS2Point(SF)
        #     if point:
        #         (x, y) = point
        #         break
        #     if time.time() - start > seconds:
        #         raise RuntimeError('func click: timeout(%.2fs), target(%s) not found' %(seconds, SF))
            # log.warn('image file(%s) not found retry' %(SF))
            # time.sleep(1)
        log.info('Click %s point: (%d, %d)', SF, x, y)
        self.dev.touch(x, y)

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

    def close(self):
        '''
        Release resouces
        '''
        pass

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
        return self.dev.start(self.appname, s.get(self._device))
    
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

