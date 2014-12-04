--- 
title: 命令行工具
layout: post
category: overview
permalink: /overview/command_line.html
---

使用pip安装完airtest后，就可以再命令行中使用`air.test`这个命令了。等价于调用`python -mairtest`

#### gui
WEB GUI客户端，主要用于截图和调试

    air.test gui --workdir='.' 

workdir默认当前目录，截图也全部保存在这个下面。

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

#### watch
监控cpu，内存数据。内存数据分为PSS，RSS，VSS。如果不清楚可以看[这篇文章](/wikipedia/memory.html)

连接手机后，运行`air.test watch -h -p com.netease.h15` 会出现下面的信息，默认每3s更新一次，`Ctrl+C`终止。

其中`com.netease.h15`是包名。-h是以人类可读的方式显示大小。更多的参数可以从`--help`中找到。


    TIME        CPU         PSS         RSS         VSS
    10:32:04    0.6         90.4 MB     126.1 MB    960.3 MB
    10:32:07    2.325       90.5 MB     126.2 MB    960.3 MB
    10:32:10    2.325       90.5 MB     126.3 MB    960.3 MB
    10:32:13    2.325       90.6 MB     126.4 MB    960.3 MB
    10:32:16    2.25        90.6 MB     126.4 MB    960.3 MB
    10:32:19    2.25        90.7 MB     126.5 MB    960.3 MB
    10:32:22    3.25        90.8 MB     126.5 MB    960.3 MB
    Signal INT catched !!!

