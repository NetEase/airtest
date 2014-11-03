--- 
title: 安装
layout: post
category: deployment
permalink: /deployment/installing.html
---

#### Windows
Windows need python2.7 32bit. <a style="color:red">Remember 32bit. not 64.</a>

从百度网盘下载安装依赖的软件包：

    网址：http://pan.baidu.com/s/1eQFyg4E
    密码: dt77

软件包中包含有：

    1. python-2.7.7-32bit
    2. pyparsing
    3. numpy
    4. dateutil
    5. matplotlib
    6. pillow
    7. pip
    8. setuptools
    9. opencv

上述安装完后，打开命令行，继续安装两个软件包

    easy_install -i http://mt.nie.netease.com:3141/simple/ androidviewclient    
    pip install -U -i http://mt.nie.netease.com:3141/simple/ airtest


最后下载adb.exe客户端 - [下载地址](ftp://mt.nie.netease.com/airtest-win-res/adb.zip),下好解压后放到PATH下, 软件[来源](http://adbshell.com/download/download-adb-for-windows.html)

#### Mac OSX
一键安装脚本

    bash -c "$(curl -s http://git.mt.nie.netease.com/hzsunshx/airtest/raw/master/scripts/mac_install.sh)"

或者手动安装，首先[安装brew](http://brew.sh/)

    brew install python
    brew install node && npm install -g appium
    brew tap homebrew/science && brew install opencv
    brew tap Homebrew/python && brew install pillow
    pip install Appium-Python-Client
    easy_install -i http://mt.nie.netease.com:3141/simple/ androidviewclient

大多数出错的地方时出现在opencv的安装上。安装完后，运行下面的代码，看看是否正常

    python -m -c 'import cv2'

如果报错，跑下下面几个命令可能会修复

    brew uninstall opencv
    brew install python
    brew link python
    brew install opencv

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>

#### 其他说明
1. Android上已经支持特殊字符的输入，运行airtest时会自动安装一个输入法软件。感谢开源项目<https://github.com/senzhk/ADBKeyBoard> [软件地址](http://mt.nie.netease.com/files/airtest-android-res/adb-keyboard.apk)

2. airtest开发版安装方法，需要下载Git客户端。windows版git[点此下载](ftp://mt.nie.netease.com/airtest-win-res/Git-1.9.4-preview20140815.exe)

        pip install -U git+http://git.mt.nie.netease.com/hzsunshx/airtest.git



