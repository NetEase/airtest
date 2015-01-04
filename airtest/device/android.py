#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import re
import subprocess
import StringIO
from functools import partial

from com.dtmilano.android.viewclient import ViewClient 

from .. import patch, base

DEBUG = os.getenv("AIRDEBUG")=="true"
log = base.getLogger('android')

__dir__ = os.path.dirname(os.path.abspath(__file__))

def _get_meminfo(serialno, package):
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
            if values[3].isdigit() and values[4].isdigit():
                ret.update(dict(VSS=int(values[3]), RSS=int(values[4])))
            else:
                ret.update(dict(VSS=-1, RSS=-1))
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

def _get_cpuinfo(serialno, package):
    '''
    @param package(string): android package name
    @return float: the cpu usage
    '''
    command = 'adb -s %s shell dumpsys cpuinfo' % serialno
    cpu_info = base.check_output(command).splitlines()
    try:
        xym_cpu = filter(lambda x: package in x, cpu_info)[0].split()[0]
        cpu = float(xym_cpu[:-1])
        return cpu
    except IndexError:
        log.error("cpu_info error")
        return 0

class Monitor(object):
    def __init__(self, serialno, pkgname):
        self._sno = serialno 
        self._pkg = pkgname
        def _adb(*args):
            return subprocess.check_output(['adb', '-s', self._sno] + list(args))
        self.adb = _adb
        self.adbshell = partial(_adb, 'shell')

    @patch.run_once
    def ncpu(self):
        ''' number of cpu '''
        output = self.adbshell('cat', '/proc/cpuinfo')
        matches = re.compile('processor').findall(output)
        return len(matches)

    def cpu(self):
        ''' cpu usage, range must be in [0, 100] '''
        for line in StringIO.StringIO(self.adbshell('dumpsys', 'cpuinfo')):
            line = line.strip()
            # 0% 11655/im.yixin: 0% user + 0% kernel / faults: 10 minor
            if '/'+self._pkg+':' in line:
                return float(line.split()[0][:-1])/self.ncpu()
        return None

    def memory(self):
        '''
        @description details view: http://my.oschina.net/goskyblue/blog/296798

        @param package(string): android package name
        @return dict: {'VSS', 'RSS', 'PSS'} (unit KB)
        '''
        ret = {}
        # VSS, RSS
        for line in StringIO.StringIO(self.adbshell('ps')):
            if line and line.split()[-1] == self._pkg:
                # USER PID PPID VSIZE RSS WCHAN PC NAME
                values = line.split()
                if values[3].isdigit() and values[4].isdigit():
                    ret.update(dict(VSS=int(values[3]), RSS=int(values[4])))
                else:
                    ret.update(dict(VSS=-1, RSS=-1))
                break
        else:
            log.error("mem get: adb shell ps error")
            return {}

        # PSS
        memout = self.adbshell('dumpsys', 'meminfo', self._pkg)
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

class Device(object):
    def __init__(self, serialno=None):
        self._snapshot_method = 'adb'
        print 'SerialNo:', serialno

        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.setReconnect(True) # this way is more stable

        self.vc = ViewClient(self.adb, serialno, autodump=False)
        self._devinfo = self.getdevinfo()

        print 'ProductBrand:', self._devinfo['product_brand']
        print 'CpuCount: %d' % self._devinfo['cpu_count']
        print 'TotalMem: %d MB' % self._devinfo['mem_total']
        print 'FreeMem: %d MB' % self._devinfo['mem_free']

        try:
            if self.adb.isScreenOn():
                self.adb.wake()
        except:
            pass

        width, height = self.shape()
        width, height = min(width, height), max(width, height)
        self._airnative = '/data/local/tmp/air-native'
        self._init_airnative()
        self._init_adbinput()

    def _init_airnative(self):
        ''' install air-native '''
        serialno = self._serialno
        def sh(*args):
            args = ['adb', '-s', serialno] + list(args)
            return subprocess.check_output(args)

        airnative = os.path.join(__dir__, '../binfiles/air-native')
        sh('push', airnative, self._airnative)
        sh('shell', 'chmod', '755', self._airnative)

    def _init_adbinput(self):
        apkfile = os.path.join(__dir__, '../binfiles/adb-keyboard.apk')
        pkgname = 'com.android.adbkeyboard'
        if not self.adb.shell('pm path %s' %(pkgname)).strip():
            print 'Install adbkeyboard.apk input method'
            subprocess.call(['adb', '-s', self._serialno, 'install', '-r', apkfile])

    def snapshot(self, filename):
        ''' save screen snapshot '''
        if self._snapshot_method == 'adb':
            log.debug('start take snapshot(%s)'%(filename))
            pil = self.adb.takeSnapshot(reconnect=True)
            pil.save(filename)
        elif self._snapshot_method == 'screencap':
            tmpname = '/data/local/tmp/airtest-tmp-snapshot.png'
            self.adb.shell('screencap -p '+tmpname)
            os.system(' '.join(('adb', '-s', self._serialno, 'pull', tmpname, filename)))
        else:
            raise RuntimeError("No such snapshot method: [%s]" % self._snapshot_method)


    def touch(self, x, y, duration=0.1):
        '''
        same as adb -s ${SERIALNO} shell input tap x y
        '''
        assert duration >= 0
        self.adb.shell('{cmd} -runjs="tap({x}, {y}, {dur})"'.format(
            cmd=self._airnative, x=x, y=y, dur=int(duration*1000)))

    def drag(self, (x0, y0), (x1, y1), duration=0.5):
        '''
        Drap screen
        '''
        self.adb.shell('{cmd} -runjs="drag({x0}, {y0}, {x1}, {y1}, {steps}, {dur})"'.format(
            cmd=self._airnative, x0=x0, y0=y0, x1=x1, y1=y1, steps=10, dur=int(duration*1000)))
        # self.adb.drag((x0, y0), (x1, y1), duration)

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

    def meminfo(self, appname):
        '''
        Retrive memory info for app
        @param package(string): android package name
        @return dict: {'VSS', 'RSS', 'PSS'} (unit KB)
        '''
        return _get_meminfo(self._serialno, appname)

    def cpuinfo(self, appname):
        '''
        @param package(string): android package name
        @return dict: {'total': float, 'average': float}
        '''
        total = _get_cpuinfo(self._serialno, appname)
        return dict(total=total, ncpu=self._devinfo['cpu_count'])

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
