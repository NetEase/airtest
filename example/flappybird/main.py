#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
flappybird test example
'''

import sys
#sys.path.insert(0, 'Z:\workspace\pyairtest')
import os
import airtest

#reload(airtest)

serialno = ''

def test():
    app = airtest.connect(serialno)

    app.sleep(1)
    app.setThreshold(0.1)
    app.click('start.png')
    app.sleep(2)
    w, h = app.shape()
    app.touch(w*0.5, h*0.5)
    app.sleep(0.5)
    app.touch(w*0.5, h*0.5)

    #app.sleep(4)
    #app.setThreshold(0.5)
    #assert app.exists('gameover.png')

if __name__ == '__main__':
    serialno = os.getenv('SERIALNO', default='4d005f1f9df03107')
    print 'SERIALNO:', serialno
    test()
