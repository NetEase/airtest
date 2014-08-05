#!/usr/bin/env python
# -*- coding: utf-8 -*-

#coding: utf-8
#
#__all__=['devsuit', 'android', 'image', 'base', 'patch', 'ios', 'device']

import time
import subprocess

from airtest import devsuit

__version__ = time.strftime('0.2.%m%d')

ANDROID = 'android'
IOS = 'ios'
WINDOWS='windows'
SEPRATOR = '::'

def connect(phoneno, appname=None, device='android', monitor=True, logfile='log/airtest.log'):
    '''
    Connect device
    '''
    if  device == ANDROID:
        from airtest.device import android
        subprocess.call(['adb', 'start-server'])
        if not phoneno:
            phoneno = [d for d, t in getDevices() if t == 'device'][0]
        devClass = android.Device
    elif device == IOS:
        from airtest.device import ios
        devClass = ios.Device
    elif device == WINDOWS:
        from airtest.device import windows
        devClass = windows.Device
    elif device == 'dummy': # this class is only for test
        from airtest.device import dummy
        devClass = dummy.Device 
    else:
        raise RuntimeError('device type not recognize')

    return devsuit.DeviceSuit(device, devClass, phoneno, 
            appname=appname, logfile=logfile, monitor=monitor)

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
            (phoneno, state) = ss
            result.append((phoneno, state))
    return result
