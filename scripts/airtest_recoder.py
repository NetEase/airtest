#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 2014/07/02 by codeskyblue
#
'''
convert adb event to air.test program
usage is simple:
    adb shell getevent -l | python airtest_recorder.py
'''

import sys
import time
import subprocess
import re

dev = '/dev/input/event1'

def getRawShape():
    output = subprocess.check_output('adb shell getevent -p '+dev, shell=True)
    re.compile(r'0035.*max (\d+)')
    max_x = re.search(r'0035.*max (\d+)', output).group(1)
    max_y = re.search(r'0036.*max (\d+)', output).group(1)
    return max_x, max_y

def getShape():
    rsRE = re.compile('\s*mRestrictedScreen=\(\d+,\d+\) (?P<w>\d+)x(?P<h>\d+)')
    for line in subprocess.check_output('adb shell dumpsys window', shell=True).splitlines():
        m = rsRE.match(line)
        if m:
            return m.groups()
    raise RuntimeError('Couldn\'t find mRestrictedScreen in dumpsys')

def getScale():
    rawx, rawy = getRawShape()
    w, h = getShape()
    return float(rawx)/float(w), float(rawy)/float(h)

def getDeviceId():
    output = subprocess.check_output('adb devices', shell=True)
    match = re.search(r'([\w\d]+)\s+device\s*$', output)
    if match:
        return match.group(1)
    raise RuntimeError("Couldn't find avaliable device")

def main():
    xs, ys = [], []
    lastOper = ''
    touchStart = 0
    start = time.time()

    scaleX, scaleY = getScale()
    deviceId = getDeviceId()

    print "import airtest\napp = airtest.connect('%s')\n" %(deviceId)

    # plen()
    while True:
        line = sys.stdin.readline()
        if not line.startswith('/dev/input/event1'):
            continue
        channel, event, oper, value = line.split()
        # print event, oper, value#int(value, 16)
        value = int(value, 16)
        if oper == 'SYN_REPORT':
            continue
        
        if oper == 'ABS_MT_POSITION_X':
            xs.append(value)
        elif oper == 'ABS_MT_POSITION_Y':
            ys.append(value)
        elif oper == 'SYN_MT_REPORT':
            if lastOper == oper:
                xs = map(lambda x: x/scaleX, xs)
                ys = map(lambda y: y/scaleY, ys)
                if len(xs) != 0 and len(ys) != 0: # something went wrong
                    (x1, y1), (x2, y2) = (xs[0], ys[0]), (xs[-1], ys[-1])
                    dist = ((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))**0.5

                    duration = time.time()-touchStart
                    # print 'Duration:', duration
                    if dist < 50:
                        print 'app.touch(%d, %d)' %(x1, y1)
                    else:
                        print 'app.drag((%d, %d), (%d, %d))' %(x1, y1, x2, y2)
                xs, ys = [], []
            else:
                if len(xs) == 1:
                    print 'app.sleep(%.1f)' % float(time.time()-start)
                    start = time.time()
                    touchStart = time.time()      
        lastOper = oper

if __name__ == '__main__':
    main()
