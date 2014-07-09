#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os

from airtest import base
from appium import webdriver

DEBUG = os.getenv("DEBUG")=="true"
log = base.getLogger('ios')

def getMem(serialno, package):
    '''
    @param package(string): android package name
    @return float: the memory, unit MB
    '''
    pass


def getCpu(serialno, package):
    '''
    @param package(string): android package name
    @return float: the cpu usage
    '''
    pass


# from zope.interface.declarations import implementer
# from airtest import interface

#@implementer(interface.IDevice)
class Device(object):
    def __init__(self, serialno=None):
        self.url = 'http://127.0.0.1:4723/wd/hub'
        self.driver = webdriver.Remote(
            command_executor=self.url,
            desired_capabilities={
                'platformName': 'iOS'
            }
        )

    def snapshot(self, filename):
        ''' save screen snapshot '''
        log.debug('start take snapshot')
        self.driver.save_screenshot(filename)
        log.debug('finish take snapshot and save to '+filename)

    def touch(self, x, y, eventType=None):
        '''
        touch screen at (x, y)
        multi finger operation not provided yet
        '''
        eventType=adbclient.DOWN_AND_UP
        log.debug('touch position %s', (x, y))
        self.driver.tap([(x, y)])

    def drag((x1, y1), (x2, y2), duration=0):
        '''
        Simulate drag from (x1, y1) to (x2, y2)
        multi finger operation not provided yet
        '''
        log.debug('drag from (%s, %s) to (%s, %s)' % (x1, y1, x2, y2))
        self.driver.swipe(x1, y1, x2, y2, duration)

    def shape(self):
        ''' 
        Get screen width and height 
        '''
        screen_size = self.driver.get_window_size()
        width, height = screen_size["width"], screen_size["height"]
        return (width, height)

    def type(self, text):
        '''
        Input some text

        @param text: string (text want to type)
        '''
        print "not provided yet on ios"

    def getMem(self, appname):
        print "not provided yet on ios"
        return getMem(self._serialno, appname)

    def getCpu(self, appname):
        print "not provided yet on ios"
        return getCpu(self._serialno, appname)

