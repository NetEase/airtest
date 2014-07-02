#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
flappybird test example
'''

import sys
#sys.path.insert(0, 'Z:\workspace\pyairtest')
import os
import airtest

def main():
    serialno, pkgname = os.getenv('SERIALNO'), os.getenv('PKGNAME')
    print 'SERIALNO:', serialno
    print 'PKGNAME:', pkgname

    app = airtest.connect(serialno, pkgname)

    app.sleep(1)
    app.setThreshold(0.1)
    app.click('start.png')
    app.sleep(2)
    w, h = app.shape()
    app.touch(w*0.5, h*0.5)
    app.sleep(0.03)
    app.touch(w*0.5, h*0.5)
    app.sleep(0.03)
    app.touch(w*0.5, h*0.5)

    app.sleep(4)
    #app.setThreshold(0.5)
    #assert app.exists('gameover.png')

if __name__ == '__main__':
    main()
