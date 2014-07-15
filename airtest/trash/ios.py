#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
iphone and ipad
'''

import os
import time
from PIL import Image

# from airtest import patch
from airtest import image
from airtest import base
from appium import webdriver

log = base.getLogger('ios')

#@patch.record()
class IosDevice(object):
    def __init__(self):
        self._imgdir = None
        self._last_point = None
        self.url = 'http://127.0.0.1:4723/wd/hub'

        log.debug("IosDevice start connecting...it may take a minute")
        self.driver = self._connect()

        self.width, self.height = self._getShape()
        self._getShapeReal()
        log.debug('IosDevice connected: width:{width}, height:{height}'.format(
            width=self.width, height=self.height))

    def _connect(self):
        return webdriver.Remote(
            command_executor=self.url,
            desired_capabilities={
                'platformName': 'iOS'
            }
        )

    def _imgfor(self, name):
        if self._imgdir:
            return os.path.join(self._imgdir, name)
        return name

    def _getShape(self):
        screen_size = self.driver.get_window_size()
        width, height = screen_size["width"], screen_size["height"]
        return (width, height)

    def _getShapeReal(self):
        screen_shot = self.takeSnapshot()
        img = Image.open(screen_shot)
        self.width_real, self.height_real = img.size
        log.debug('IosDevice real resolution: width:{width}, height:{height}'.format(
            width=self.width_real, height=self.height_real))

    def _saveScreen(self, filename):
        filename = base.random_name(filename)
        self.takeSnapshot(filename)
        return filename
    
    def shape(self):
        ''' get screen width and height '''
        return self._getShape()

    def _cvtXY(self, x, y):
        """convert x,y from device real resolution to action input resolution"""
        x_input = x * self.width / self.width_real
        y_input = y * self.height / self.height_real
        print "cvt %s,%s to %s,%s" % (x, y, x_input, y_input)
        return (int(x_input), int(y_input))

    def setImageDir(self, imgdir='.'):
        self._imgdir = imgdir

    def takeSnapshot(self, filename="lastest.png"):
        ''' @return PIL image '''
        log.debug('take snapshot and save to '+filename)
        self.driver.save_screenshot(filename)
        return filename

    def startActivity(self, appname):
        log.debug("app already started in ios")

    def touch(self, x, y, eventType=None):
        log.debug('touch position %s', (x, y))
        self.driver.tap([(x, y)])

    def wait(self, imgfile, interval=0.5, max_retry=5):
        '''
        wait until some picture exists
        '''
        pt = base.wait_until(self.where, args=(imgfile,), interval=interval, max_retry=max_retry)
        if not pt:
            raise RuntimeError('wait fails')
        self._last_point = pt
        return

    def where(self, imgfile):
        '''
        find image location
        @return list of find points
        '''
        screen = self._saveScreen('where-XXXXXXXX.png')
        pts = _image_locate(screen, imgfile)
        return pts and pts[0]

    def exists(self, imgfile):
        return True if self.where(imgfile) else False

    def click(self, imgfile=None, delay=1.0):
        '''
        '''
        self.sleep(delay)
        if imgfile:
            self.takeSnapshot('screenshot.png')
            log.debug('locate postion where to touch')
            pos = _image_locate('screenshot.png', self._imgfor(imgfile))[0]
        else:
            pos = self._last_point
        (x, y) = (pos[0], pos[1])
        x, y = self._cvtXY(x, y)
        print 'click', imgfile, x, y
        # check if horizontal
        w, h = self._getShape()
        if w > h:
            log.debug('Screen rotate, width(%d), height(%d)', w, h)
            log.debug('(%d, %d) -> (%d, %d)', x, y, y, h-x)
            x, y = y, h-x
        self.touch(x, y)

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

    def sleep(self, secs=1.0):
        '''
        Sleeps for the specified number of seconds

        @param secs: float (number of seconds)
        @return None
        '''
        log.debug('SLEEP %ds', secs)
        time.sleep(secs)

    def keyevent(self, name):
        log.error("cannot use on ios")

    def home(self):
        log.error("cannot use on ios")
        
    def enter(self):
        log.error("cannot use on ios")

    def type(self, text):
        """how to do it on ios?"""
        log.error("cannot use on ios")
        return False

    def drag(self, f, to):
        ''' 
        @param duration: duration of the event in ms
        '''
        # the duration seems not working. no matter how larger I set, nothing changes.
        duration=500
        variable = {}
        def to_point(raw):
            global screen
            if isinstance(raw, list) or isinstance(raw, tuple):
                return raw
            if isinstance(raw, basestring):
                screen = variable.get('screen')
                if not screen:
                    variable['screen'] = self._saveScreen('where-XXXXXXXX.png')
                return _image_locate_one(variable['screen'], self._imgfor(raw))
            else:
                raise RuntimeError('invalid type')
        fpt, tpt = to_point(f), to_point(to)
        return self.driver.swipe(fpt[0], fpt[1], tpt[0], tpt[1], duration)

def _image_locate_one(orig, query):
    pts = _image_locate(orig, query)
    if len(pts) > 1:
        raise RuntimeError('too many same query images')
    if len(pts) == 0:
        raise RuntimeError('query image not found')
    return pts[0]

def _image_locate(origin_file, query_file):
    '''
    image match
    '''
    log.debug('search image(%s) from(%s)', query_file, origin_file)
    pts = image.locate_image(origin_file, query_file)
    return pts


if __name__ == '__main__':
    d = IosDevice()
    d.click("start.png")
    for i in range(10):
        print "retry:", i
        d.drag((160, 300), (290, 300))
        print d.exists("retry.png")
        d.drag((290, 300), (160, 300))
        d.drag((160, 300), (30, 300))
        d.wait("retry.png", interval=2)
        if d.exists("retry.png"):
            d.click("retry.png")

