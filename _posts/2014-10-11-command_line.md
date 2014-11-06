--- 
title: 命令行工具
layout: post
category: overview
permalink: /overview/command_line.html
---

使用pip安装完airtest后，就可以再命令行中使用`air.test`这个命令了。等价于调用`python -mairtest`

#### install
	air.test install [apk-file] # 如果不指定apk-file,便会去查找air.json这个文件
	air.test install --no-start [apk-file]  # 安装完后，不自动启动

air.json文件的内容格式如下

	{"apk": "flappybird.apk"}

#### uninstall
	air.test uninstall [apk-file] # 方法基本同install，除了没有--no-start这个参数

#### inspect
查看一个apk包的package名和activity。

	air.test inspect <apk-file>

#### log2html
将airtest运行后的log文件转化成html。

	air.test log2html --listen --port 8800 --logfile log/airtest.log outdir

或者简写成

	air.test log2html --listen outdir

打开浏览器，访问localhost:8800可以查看报告

#### snapshot
截取屏幕图像，扩展名支持png和jpg

	air.test snapshot --out snapshot.png

