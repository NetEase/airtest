#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
nija test example
'''

import sys
import os
import airtest

serialno = os.getenv('AIRTEST_PHONENO')
appname  = os.getenv('AIRTEST_APPNAME')
device = os.getenv('DEVICE') or 'android'

app = airtest.connect(serialno, appname=appname, device=device)
print 'connected'

app.stop()
app.sleep(4)
app.start()

app.sleep(5) # wait for start loading
app.click('youke.png') # 游客入口
app.sleep(15) # wait for loading

# 领取奖励
if app.clickIfExists('reward.png'):
    app.click(app.center())
app.sleep(5)

# 关闭公告板
if app.exists('pubboard.png'):
    app.click('close_pub.png')
    
if app.clickIfExists('match_confirm.png'):
    app.sleep(8) # wait for loading

if app.clickIfExists('receiveit.png'):
    app.click('confirm.png')

position = app.wait('beizhan.png')
app.click(position)
app.sleep(2)
app.click(position)
print 'NOW loading into game'
