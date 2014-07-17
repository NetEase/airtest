#!/usr/bin/env python
# -*- coding: utf-8 -*-


from zope.interface import Interface

#def getNetFlow(appname=None)
#    Get current network flow 

class IDevice(Interface):
    ''' Interface documentation '''

    def snapshot(filename):
        ''' Capture device screen '''

    def touch(x, y):
        ''' Simulate touch '''

    def drag((x1, y1), (x2, y2)):
        ''' Simulate drag '''

    def type(text):
        ''' Type text into device '''

    def shape():
        ''' Return (width, height) '''

    def getCpu(appname):
        ''' Return cpu: float (Cpu usage for app) '''

    def getMem(appname):
        ''' Return mem: float (unit MB, memory usage for app) '''

