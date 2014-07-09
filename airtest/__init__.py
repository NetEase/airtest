#!/usr/bin/env python
# -*- coding: utf-8 -*-

#coding: utf-8
#
__all__=['android', 'image', 'base', 'patch', 'ios']

import subprocess

ANDROID = 'android'
IOS = 'ios'
SEPRATOR = '::'

def connect(serialno=None, pkgname=None, device='android'):
    '''
    connect to a mobile phone
    '''   
    if device == ANDROID:
        from airtest import android
        assert serialno != None
        return android.AndroidDevice(serialno=serialno, pkgname=pkgname)
    elif device == IOS:
        from airtest import ios
        return ios.IosDevice() # FIXME(not finished)

def getDevices(device='android'):
    ''' return devices list '''
    subprocess.call(['adb', 'start-server'])
    output = subprocess.check_output(['adb', 'devices'])
    result = []
    for line in output.splitlines()[1:]:
        ss = line.strip().split()
        if len(ss) == 2:
            (serialno, state) = ss
            result.append((serialno, state))
    return result
