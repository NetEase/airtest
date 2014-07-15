#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
flappybird test example
'''

import sys
#sys.path.insert(0, 'Z:\workspace\pyairtest') # this for debug
import os
import airtest

def main():
    serialno = os.getenv('AIRTEST_PHONENO') or 'yykksj1231'
    appname = os.getenv('APPNAME') or 'com.dotgears.flappybird'
    print 'SERIALNO:', serialno
    print 'APPNAME:', appname

    app = airtest.connect(serialno, appname=appname)

    #app.stop()
    #app.start()

    app.sleep(2)

    #app.globalSet({'threshold': 0.1})
    app.click('start.png')
    w, h = app.shape()
    middle_point = (w*0.5, h*0.5)
    for i in range(5):
        app.click(middle_point)
        app.sleep(0.02)
    app.sleep(4)
    #assert app.exists('gameover.png')

if __name__ == '__main__':
    main()
