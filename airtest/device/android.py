#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import re
import subprocess

from airtest import base
from com.dtmilano.android.viewclient import ViewClient 
from com.dtmilano.android.viewclient import adbclient

DEBUG = os.getenv("AIRDEBUG")=="true"
log = base.getLogger('android')

__dir__ = os.path.dirname(os.path.abspath(__file__))

def getMem(serialno, package):
    '''
    @description details view: http://my.oschina.net/goskyblue/blog/296798

    @param package(string): android package name
    @return dict: {'VSS', 'RSS', 'PSS'} (unit KB)
    '''
    command = 'adb -s %s shell ps' %(serialno)
    output = base.check_output(command)
    ret = {}
    for line in str(output).splitlines():
        if line and line.split()[-1] == package:
            # USER PID PPID VSIZE RSS WCHAN PC NAME
            values = line.split()
            ret.update(dict(VSS=int(values[3]), RSS=int(values[4])))
            break
    else:
        log.error("mem get: adb shell ps error")
        return {}
    psscmd = 'adb -s %s shell dumpsys meminfo %s' %(serialno, package)
    memout = base.check_output(psscmd)
    pss = 0
    result = re.search(r'\(Pss\):(\s+\d+)+', memout, re.M)
    if result:
        pss = result.group(1)
    else:
        result = re.search(r'TOTAL\s+(\d+)', memout, re.M)
        if result:
            pss = result.group(1)
    ret.update(dict(PSS=int(pss)))
    return ret

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
        print 'SerialNo:', serialno

        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.setReconnect(True) # this way is more stable

        self.vc = ViewClient(self.adb, serialno, autodump=False)
        self._devinfo = self.getdevinfo()

        print 'ProductBrand:', self._devinfo['product_brand']

        try:
            if self.adb.isScreenOn():
                self.adb.wake()
        except:
            pass

        width, height = self.shape()
        width, height = min(width, height), max(width, height)
        self._airtoolbox = '/data/local/tmp/airtoolbox'
        self._init_airtoolbox()
        self._init_adbinput()

    def _init_airtoolbox(self):
        ''' init airtoolbox '''
        serialno = self._serialno
        def sh(*args):
            args = ['adb', '-s', serialno] + list(args)
            return subprocess.check_output(args)

        out = sh('shell','sh','-c', 'test -x {tbox} && {tbox} version'.format(
            tbox=self._airtoolbox))
        out = out.strip()
        print 'AirToolbox: '+out.strip()
        version_file = os.path.join(__dir__, '../binfiles/airtoolbox.version')
        version = open(version_file).read().strip()
        if not out.endswith(version):
            print 'upgrade: airtoolbox (ver %s)...' %(version)
            toolbox = os.path.join(__dir__, '../binfiles/airtoolbox')
            sh('push', toolbox, self._airtoolbox)
            sh('shell', 'chmod', '755', self._airtoolbox)

    def _init_adbinput(self):
        apkfile = os.path.join(__dir__, '../binfiles/adb-keyboard.apk')
        pkgname = 'com.android.adbkeyboard'
        if not self.adb.shell('pm path %s' %(pkgname)).strip():
            print 'Install adbkeyboard.apk input method'
            subprocess.call(['adb', '-s', self._serialno, 'install', '-r', apkfile])

    def snapshot(self, filename):
        ''' save screen snapshot '''
        log.debug('start take snapshot(%s)'%(filename))
        pil = self.adb.takeSnapshot(reconnect=True)
        return pil.save(filename)
        # try:
        #     if self._useScreencap:
        #         raise IOError('trigger error, inorder to use other takesnapshot way')
        #     pil = self.adb.takeSnapshot(reconnect=True)
        #     pil.save(filename)
        # except:
        #     tmpname = '/sdcard/airtest-screen.png'
        #     self.adb.shell('screencap -p '+tmpname)
        #     os.system(' '.join(('adb', '-s', self._serialno, 'pull', tmpname, filename)))
        #     self.adb.shell('rm '+tmpname)
        #     log.debug('use Screencap to takesnapshot '+filename)
        # else:
        #     log.debug('finish take snapshot and save to '+filename)

    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        '''
        same as adb -s ${SERIALNO} shell input tap x y
        '''
        if eventType == 'down':
            self.adb.shell('{toolbox} input tapdown {x} {y}'.format(
                toolbox=self._airtoolbox, x=x, y=y))
            log.debug('touch down position %s', (x, y))
        elif eventType == 'up':
            self.adb.shell('{toolbox} input tapup'.format(
                toolbox=self._airtoolbox, x=x, y=y))
            log.debug('touch up position %s', (x, y))
        elif eventType == 'down_and_up':
            log.debug('touch position %s', (x, y))
            self.adb.touch(x, y) 
        else:
            raise RuntimeError('unknown eventType: %s' %(eventType))

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

    def _type_raw(self, text):
        #adb shell ime enable com.android.adbkeyboard/.AdbIME
        #adb shell ime set com.android.adbkeyboard/.AdbIME
        #adb shell am broadcast -a ADB_INPUT_TEXT --es msg '你好嗎? Hello?'
        #adb shell ime disable com.android.adbkeyboard/.AdbIME
        adbkeyboard = ['com.android.adbkeyboard/.AdbIME']
        ime = ['adb', '-s', self._serialno, 'shell', 'ime']
        subprocess.call(ime+['enable']+adbkeyboard)
        subprocess.call(ime+['set']+adbkeyboard)
        subprocess.call(['adb', '-s', self._serialno, 'shell', 'am', 'broadcast', '-a', 'ADB_INPUT_TEXT', '--es', 'msg', text])
        subprocess.call(ime+['disable']+adbkeyboard)

    def type(self, text):
        '''
        Input some text

        @param text: string (text want to type)
        '''
        log.debug('type text: %s', repr(text))
        first = True
        for s in text.split('\n'):
            if first:
                first=False
            else:
                self.adb.press('ENTER')
            if not s:
                continue
            self._type_raw(s)

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
