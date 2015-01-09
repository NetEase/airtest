--- 
title: airtest结合unittest
layout: post
category: links
permalink: /links/unittest.html
---


airtest提供了控制手机的方法，unittest善于组织测试代码。 

通过unittest可以将测试的功能点分成一个个的测试函数。 

unittest有两个函数setUp, tearDown. 分别在每个测试函数的开始和结束时调用。分别写开始程序和结束程序。 

先看样例代码，这是一个简单的登陆测试(代码可以在[http://git.mt.nie.netease.com/hzsunshx/h15-example](http://git.mt.nie.netease.com/hzsunshx/h15-example])下载到)。


    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    
    import os
    import unittest
    import airtest
    
	# adb devices可以查到
    devno = os.getenv('AIRTEST_DEVNO') or 'af89123lkjv'
    appname = os.getenv('AIRTEST_APPNAME') or 'com.netease.h15'
    device = os.getenv('AIRTEST_DEVICE') or airtest.ANDROID
    
    app = airtest.connect(devno, appname=appname, device=device, monitor=False)
    app.globalSet(image_match_method='template', threshold=0.7)
    
    class TestFunctions(unittest.TestCase):
        def setUp(self):
			activity = '.Main' # 不用的应用activity不一样，用air.test inspect <apkfile> 可以查看activity
            os.system('adb shell am start -s -N ' + appname + '/'+activity)
    
        def tearDown(self):
			os.system('adb shell am force-stop ' + appname)
    
        def _randname(self, length=6):
            import random, string
            s = ''
            for i in range(length):
                s += random.choice(string.letters)
            return s
            
        def _register(self):
            user, passwd = self._randname(), self._randname()
            app.click('login_account.png')
            app.type(user+'\n')
            app.click('login_password.png')
            app.type(passwd+'\n')
            app.click('register.png')
            app.sleep(1)
            app.click('login.png')
            app.sleep(2)
            app.wait('zhengqi.png')
            
        def test_login(self):
            self._register()
            app.takeSnapshot('final-snapshot.png')
    
    if __name__ == '__main__':
        unittest.main() 
