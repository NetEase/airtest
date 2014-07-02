#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
flappybird test example
'''

import sys
import os
import airtest

serialno = os.getenv('SERIALNO')
app = airtest.connect(serialno)

app.drag('up.png', 'down.png')
#app.drag((851, 1474), (436, 1404))
#app.sleep(1)
#app.setThreshold(0.1)
#app.click('start.png')
#app.sleep(2)
#w, h = app.shape()
#app.touch(w*0.5, h*0.5)
#app.sleep(0.06)
#app.touch(w*0.5, h*0.5)
