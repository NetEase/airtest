#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import re

from airtest import base
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
        #log.info("mem: %.2f" % mem)
        return mem
    except IndexError:
        log.error("mem error")
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
        #log.info("cpu: %.2f" % cpu)
        return cpu
    except IndexError:
        log.error("cpu_info error")
        return 0

# from zope.interface.declarations import implementer
# from airtest import interface

#@implementer(interface.IDevice)
class Device(object):
    def __init__(self, serialno=None):
        print 'S:', serialno
        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.reconnect = True # this way is more stable

        self.vc = ViewClient(self.adb, serialno)
        ViewClient.connectToDeviceOrExit()
        self._devinfo = self.getdevinfo()

        try:
            if self.adb.isLocked():
                self.adb.unlock()
        except:
            pass

    def snapshot(self, filename):
        ''' save screen snapshot '''
        log.debug('start take snapshot')
        pil = self.adb.takeSnapshot(reconnect=True)
        log.debug('finish take snapshot and save to '+filename)
        pil.save(filename)

    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        '''
        same as adb -s ${SERIALNO} shell input tap x y
        '''
        eventType=adbclient.DOWN_AND_UP
        log.debug('touch position %s', (x, y))
        self.adb.touch(x, y, eventType)

    def drag(self, (x0, y0), (x1, y1), duration=0.5):
        '''
        Drap screen
        '''
        self.adb.drag((x0, y0), (x1, y1), duration)

    def shape(self):
        ''' 
        Get screen width and height 
        '''
        width = self.adb.getProperty("display.width")
        height = self.adb.getProperty("display.height")
        return (width, height)

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

    def keyevent(self, event):
        '''
        Send keyevent by adb

        @param event: string (one of MENU, HOME, BACK)
        '''
        self.adb.shell('input keyevent '+str(event))

    def getMem(self, appname):
        return getMem(self._serialno, appname)

    def getCpu(self, appname):
        return getCpu(self._serialno, appname)/self._devinfo['cpu_count']

    def start(self, appname, extra={}):
        '''
        Start a program

        @param extra: dict (defined in air.json)
        '''
        #exec_cmd('adb', '-s', serialno, 'shell', 'am', 'start', '-n', '/'.join([package, activity]), timeout=10)
        # -S: force stop the target app before starting the activity
        self.adb.shell('am start -S -n '+appname+'/'+extra.get('activity'))

    def stop(self, appname, extra={}):
        '''
        Stop app
        '''
        self.adb.shell('am force-stop '+appname)

    def clear(self, appname, extra={}):
        '''
        Stop app and clear data
        '''
        self.adb.shell('pm clear '+appname)

    def getdevinfo(self):
        # cpu
        output = self.adb.shell('cat /proc/cpuinfo')
        matches = re.compile('processor').findall(output)
        cpu_count = len(matches)
        # mem
        output = self.adb.shell('cat /proc/meminfo')
        match = re.compile('MemTotal:\s*(\d+)\s*kB\s*MemFree:\s*(\d+)', re.IGNORECASE).match(output)
        if match:
            mem_total = int(match.group(1), 10)>>10 # MB
            mem_free = int(match.group(2), 10)>>10
        else:
            mem_total = -1
            mem_free = -1

        # brand = self.adb.getProperty('ro.product.brand')
        return {
            'cpu_count': cpu_count,
            'mem_total': mem_total,
            'mem_free': mem_free,
            'product_brand': self.adb.getProperty('ro.product.brand'),
            'product_model': self.adb.getProperty('ro.product.model')
            }
