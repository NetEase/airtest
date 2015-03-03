--- 
title: Mac安装
layout: post
category: deployment
permalink: /deployment/mac-installing.html
---

一键安装脚本

    bash -c "$(curl -s https://raw.githubusercontent.com/NetEase/airtest/master/scripts/mac_install.sh)"

或者手动安装，首先[安装brew](http://brew.sh/), 其中opencv一定不能早于python安装

    brew install python
    which python # 确认下，python的路径在 /usr/local/bin/python

    easy_install pip
    brew install node && npm install -g appium
    brew tap homebrew/science && brew install opencv
    brew tap Homebrew/python && brew install pillow
    pip install Appium-Python-Client

    pip install -U airtest #开发版安装方法，见下面

#### opencv安装检查：

    python -m -c 'import cv2'

如果报错，跑下下面几个命令可能会修复

    brew uninstall opencv
    brew install python
    brew link python
    brew install opencv

其他错误参考这个issue解决 <https://github.com/Homebrew/homebrew/issues/18877>

#### appium安装检查
    appium-doctor

### airtest开发版安装方法
    brew install git
    pip install -U git+https://github.com/netease/airtest.git
