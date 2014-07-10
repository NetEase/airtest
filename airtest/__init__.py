#!/usr/bin/env python
# -*- coding: utf-8 -*-

#coding: utf-8
#
#__all__=['devsuit', 'android', 'image', 'base', 'patch', 'ios', 'device']

import subprocess

from airtest import device
from airtest import devsuit


ANDROID = 'android'
IOS = 'ios'
SEPRATOR = '::'

def connect(serialno, appname=None, device='android'):
    '''
    Connect device
    '''
    if  device == ANDROID:
        from airtest.device import android
        devClass = android.Device
    elif device == IOS:
        from airtest.device import ios
        devClass = ios.Device
    else:
        raise RuntimeError('device type not recognize')

    return devsuit.DeviceSuit(devClass, serialno, appname=appname)

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
            (serialno, state) = ss
            result.append((serialno, state))
    return result
