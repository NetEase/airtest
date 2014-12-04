--- 
title: 快速入门
layout: post
category: overview
permalink: /overview/quick_start.html
---

下面将用一个例子说明一下怎么使用Airtest.


1. 按照安装文档 [win]({{site.baseurl}}/deployment/win-installing.html), [mac]({{site.baseurl}}/deployment/mac-installing.html)上的说明，一步步的完成安装

2. 下载[样例代码](http://git.mt.nie.netease.com/hzsunshx/flappybird): *如果没有git，[点此下载](http://goandroid.qiniudn.com/Git-1.9.4-preview20140929.exe)*

		git clone http://git.mt.nie.netease.com/hzsunshx/flappybird

3. 打开flappybird中的main.py文件，中有几行代码是

        devnum  = os.getenv('AIRTEST_DEVNO') or '4d005f1f9df03107'
        appname = os.getenv('AIRTEST_APPNAME') or 'com.dotgears.flappybird'
        device  = os.getenv('AIRTEST_DEVICE') or airtest.ANDROID

        app = airtest.connect(devnum, appname=appname, device=device)

    其中的**devnum**是手机连接电脑后，通过cmd中运行`adb devices`查看到的手机序列号。
    **appname**是apk文件的包名，可以通过询问开发人员拿到。

    在最新版的airtest中，devnum是airtest.connect中的可选参数，只有当连接设备超过1台的时候，才需要指定。
    代码可以简写成

        app = airtest.connect(appname=appname, device=device)

4. 成品代码[filename: main.py]

        import airtest
        app = airtest.connect(appname='com.dotgears.flappybird', device=airtest.WINDOWS)
        w, h = app.shape()
        app.click(w/2, h/2) # 屏幕中间点一下
        app.takeSnapshot('screen.png') # 截图保存到screen.png

5. 最后运行下，查看下效果。

    1. cmd到flappybird那个目录
    2. 运行`air.test install`。安装flappybird那个程序到手机
    3. 运行`python main.py`。运行测试代码
    4. 运行`air.test log2html --listen --port=8800 htmldir`生成测试报告。打开浏览器localhost:8800查看测试报告。
    5. 最后运行`air.test uninstall`从手机中卸载应用。

    注：

    >air.test是airtest的辅助运行工具，它依赖air.json这个文件。可以通过air.test gen flappybird.apk生成。`air.json`默认生成在当前目录。

    为了能让airtest运行的更准确，还需要参考下[配置的设置]({site.baseurl}/components/setting.html)
