#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.9.13'

ANDROID = 'android'
IOS = 'ios'
WINDOWS='windows'

ANDROIDWIFI = 'androidwifi'

# import os
# import json
import subprocess
import signal
import sys

from . import patch
from . import proto
from . import cron
from . import devsuit

def _sig_handler(signum, frame):
    print >>sys.stderr, 'Signal INT catched !!!'
    sys.exit(1)
signal.signal(signal.SIGINT, _sig_handler)


# defaultConfigFile = 'air.json'
defaultDevice = 'android'


# #
# ## ==========================================================
# #
# def _android_start(serialno, params):
#     package = params.get('package')
#     activity = params.get('activity')
#     subprocess.call(['adb', '-s', serialno, 'shell', 'am', 'start', '-n', '/'.join([package, activity])])

# def _android_stop(serialno, params):
#     package = params.get('package')
#     subprocess.call(['adb', '-s', serialno, 'shell', 'am', 'force-stop', package])

# def _windows_start(basename, params={}):
#     dir_ = params.get('dir') or '.'
#     os.system('cd /d %s && start %s' %(dir_, basename))

# def _windows_stop(basename, params={}):
#     basename = basename.lower()
#     if not basename.endswith('.exe'):
#         basename += '.exe'
#     os.system('taskkill /t /f  /im %s' %(basename))

# def _run_control(devno, device=None, action='start'):
#     device = device or defaultDevice
#     cfg = _safe_load_config(defaultConfigFile)
#     func = '_%s_%s'%(device, action)
#     if func not in globals():
#         raise RuntimeError('device(%s) %s method not exists' % (device, action))
#     return globals()[func](devno, cfg.get(device, {}))

# def start(devno, device=None):
#     _run_control(devno, device, 'start')

# def stop(devno, device=None):
#     _run_control(devno, device, 'stop')

# #
# ## ----------------------------------------------------------
# #

def _parse_addr(addr):
    '''
    通过 proto://url 拿到相应的模块和地址
    '''
    import urlparse
    p = urlparse.urlparse(addr)
    if not p.scheme:
        raise RuntimeError('device type must be specified')
    
    exec('from .device import '+p.scheme)#, p.netloc, p.path
    module = eval(p.scheme)
    # 自动查找设备
    loc = p.netloc
    if p.scheme == 'android' and not loc:
        loc = mustOneDevice()
    return module, loc, p

class Monitor(object):
    '''
    Create a new monitor
    '''
    def __init__(self, addr, appname):
        '''
        @addr: eg: android://<serialno>  or ios://127.0.0.1
        @appname: android package name or ios bundle id
        '''
        module, loc, _ = _parse_addr(addr)
        self._m = module.Monitor(loc, appname)

    def __getattr__(self, key):
        if hasattr(self._m, key):
            return getattr(self._m, key)
        raise AttributeError('Monitor object has no attribute "%s"' % key)

    # def watch(self, interval=3.0, outfd=sys.stdout):
    #     pass
    # #     if threading_lock: threading_lock.acquire()
    # #     if threading_lock: threading_lock.release()

class Device(object):
    '''
    Create a new device instance and use this instance to control device
    '''
    def __init__(self, addr, logfile=None):
        '''
        @addr: eg: android://<serialno> or ios://127.0.0.1
        '''
        module, loc, p = _parse_addr(addr)
        dev = module.Device(loc)
        self._m = devsuit.DeviceSuit(p.scheme, dev, logfile=logfile)

    def __getattr__(self, key):
        if hasattr(self._m, key):
            return getattr(self._m, key)
        raise AttributeError('Monitor object has no attribute "%s"' % key)

class _JoinClass(object):
    def __init__(self, clss):
        ''' clss ~ list:classes '''
        self._clss = clss
    def __getattr__(self, key):
        for cl in self._clss:
            if hasattr(cl, key):
                return getattr(cl, key)
        raise AttributeError('Object has no attribute "%s"' % key)

def connect(addr, appname=None, device=None, monitor=True, interval=3.0, logfile='log/airtest.log'):
    clss = []
    # compatible with old connect style
    if device:
        addr = device+'://'+addr

    dev = Device(addr, logfile)
    clss.append(dev)

    m = None
    if appname:
        m = Monitor(addr, appname)
        clss.append(m)

    c = _JoinClass(clss)

    @patch.attachmethod(c)
    def logPerformance(self):
        if not hasattr(m, 'cpu'):
            return
        print m.cpu()
        dev.log(proto.TAG_CPU, m.cpu())
        dev.log(proto.TAG_MEMORY, m.memory())

    @patch.attachmethod(c)
    def startMonitor(self):
        c.cron.start()

    @patch.attachmethod(c)
    def stopMonitor(self):
        c.cron.stop()
        print 'stop monitor'

    c.cron = cron.Crontab()
    c.cron.addfunc(c.logPerformance)
    c.cron._cycle = interval

    if monitor:
        c.startMonitor()
    
    return c

# def conn()
# def connect(devno=None, appname=None, device=None, monitor=True, logfile='log/airtest.log'):
#     '''
#     Connect device
#     @param devno: If devno is None, then get device serialno from `adb devices`
#     @param device: can be one of <android|windows|ios>
#     @param monitor: wether to enable CPU monitor
#     '''
#     if not devno:
#         devs = getDevices()
#         if not devs:
#             sys.exit('adb: No devices found')
#         if len(devs) != 1:
#             sys.exit('adb: Too many devices, need to specify phone serialno')
#         devno = devs[0][0]

#     device = device or defaultDevice
#     if  device == ANDROID:
#         from airtest.device import android
#         subprocess.call(['adb', 'start-server'])
#         if not devno:
#             devno = [d for d, t in getDevices() if t == 'device'][0]
#         devClass = android.Device
#     elif device == IOS:
#         from airtest.device import ios
#         devClass = ios.Device
#     elif device == WINDOWS:
#         from airtest.device import windows
#         devClass = windows.Device
#     elif device == 'dummy': # this class is only for test
#         from airtest.device import dummy
#         devClass = dummy.Device 
#     elif device == ANDROIDWIFI:
#         from airtest.device import androidwifi
#         devClass = androidwifi.Device
#     else:
#         raise RuntimeError('device type not recognize')

#     return devsuit.DeviceSuit(device, devClass(devno), 
#             appname=appname, logfile=logfile, monitor=monitor)

def getDevices(device='android'):
    ''' 
    @return devices list 
    '''
    subprocess.call(['adb', 'start-server'])
    output = subprocess.check_output(['adb', 'devices'])
    result = []
    for line in str(output).splitlines()[1:]:
        ss = line.strip().split()
        if len(ss) == 2:
            (devno, state) = ss
            result.append((devno, state))
    return result

def mustOneDevice():
    ''' make sure only one devices connected '''
    devs = [d for d, t in getDevices() if t == 'device']
    if len(devs) == 0:
        raise RuntimeError('no device connected')
    if len(devs) > 1:
        raise RuntimeError('must specify one device')
    return devs[0]
