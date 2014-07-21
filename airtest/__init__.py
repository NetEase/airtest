#!/usr/bin/env python
# -*- coding: utf-8 -*-

#coding: utf-8
#
#__all__=['devsuit', 'android', 'image', 'base', 'patch', 'ios', 'device']

__version__ = '0.2.0721'

import subprocess

from airtest import device
from airtest import devsuit


ANDROID = 'android'
IOS = 'ios'
WINDOWS='windows'
SEPRATOR = '::'

def connect(phoneno, appname=None, device='android'):
    '''
    Connect device
    '''
    if  device == ANDROID:
        from airtest.device import android
        devClass = android.Device
    elif device == IOS:
        from airtest.device import ios
        devClass = ios.Device
    elif device == WINDOWS:
        from airtest.device import windows
        devClass = windows.Device
    else:
        raise RuntimeError('device type not recognize')

    return devsuit.DeviceSuit(devClass, device, phoneno, appname=appname)

def getDevices(device='android'):
    ''' 
    @return devices list 
    '''
    subprocess.call(['adb', 'start-server'])
    output = subprocess.check_output(['adb', 'devices'])
    result = []
    for line in output.splitlines()[1:]:
        ss = line.strip().split()
        if len(ss) == 2:
            (phoneno, state) = ss
            result.append((phoneno, state))
    return result
