---
title: 更新日志
layout: post
category: links
permalink: /changelog.html
---
### 2015/03/03 - 0.9.16
1. 增加air.test doctor命令，用来检测可能干扰airtest正常运行的情况

### 2015/02/02 - 0.9.15
1. 修复小米手机截图时，旋转方向错误的问题

### 2015/01/22 - 0.9.14
1. android-Monitor添加了battery()

### 2015/01/22 - 0.9.13
1. bug好多，修复了一堆

### 2015/01/16 - 0.9.11
1. 配置项的改动

		rotation这个选项有很大的改动。 
		从原来的
		app.globalSet(rotation='LEFT') 
		调整为了
		app.globalSet(rotation=airtest.proto.ROTATION_90)

2. airtest.connect重写
3. 增加operation_mark这个选项
4. image match 中的auto算法，改用了[aircv](https://github.com/netease/aircv)这个库
5. 增加两个接口startApp和stopApp
6. 增加了rotation()这个接口

### 2015/01/13 - 0.9.9
1. air.test watch 增加了 --syscpu选项，来导出系统cpu占用率
	增加了SYSAVGCPU,SYSALLCPU

		TIME        CPU         PSS         RSS         VSS         SYSAVGCPU   SYSALLCPU
		15:28:34    0.025       47.3 MB     89.5 MB     965.2 MB    14.63       38.71|12.9|3.45|3.4
		15:28:37    0.025       47.3 MB     89.5 MB     965.2 MB    13.18       0.0|3.33|10.0|39.39

### 2015/01/09 - 0.9.6
1. 监控数据与设备控制命令分离
	连接方式从 airtest.connect 更新成

		m = airtest.Monitor('android://xxxx', package_name)
		m.cpu(); m.memory()

		d = airtest.Device('android://xxxx')
		d.click(position)
2. 支持ios的性能监控
		m = airtest.Monitor('ios://xxxx', package_name)

### 2014/12/29 - 0.9.3
1. airtest 两个命令 click, drag 增加 duration的支持

### 2014/12/09 - 0.9.1
1. 更新airtest的log格式
2. webgui可以查看截图中的sift特征点的数量。

### 2014/12/03 - 0.9.0
1. 添加snapshot_method到globalSet选项中，来适应部分手机截图故障问题
2. 添加webgui，方便截图和调试

### 2014/11/18 - 0.8.0
1. 添加keepCapture和releaseCapture这两个函数

### 2014/11/10 - 0.7.2
1. 部分bug修复
2. 新增air.test watch命令，用于查看内存和cpu数据
3. gh-pages分支，增加评论功能

### 2014/11/06 - 0.6.4
1. 修复androaxml.zip丢失的bug

### 2014/11/05 - 0.6.2
1. 重构air.test命令行工具
	- air.json格式简化
	- 使用click替换到docopt库
	- 去除air.test runtest, gen
	- 增加air.test inspect用于查看package和activity
2. 修复keyboard.apk没有自动安装的bug

### 2014/11/03 - 0.6.1
1. 更新说明文档
2. 建立gh-pages分支。

### 2014/09/16
1. 支持输入法的自动安装
2. 图像识别算法，分离出feature SIFT算法
3. 修正屏幕点亮的问题。多余代码清理
4. 易用性修改，如果只有一个android设备连接，可以不用指定serialno

### 2014/08/29
1. 输入法支持中文及特殊字符

### 2014/08/27
1. 支持python -mairtest 等价于 命令行的air.test
2. log2html生成的文件支持点击放大的效果。
3. 修复air.test gen命令，对于某些apk，不生效的问题。

### 2014/08/20
1. 新增airtoolbox工具（该工具可以运行在手机上，采集手机的内存，网卡信息，模拟长按的操作）
2. 完成air.test gen命令

### 2014/08/14
1. 增加app.monitor变量， 可以通过app.monitor.start() 启动监控和通过app.monitor.stop()停止监控
2. 增加fps的支持

### 2014/08/12
1. 增加image_match_method配置项，可以手动选择图形匹配算法
2. 环境变量AIRTEST_DEVNO改名为AIRTEST_PHONENO(影响范围，使用air.test命令行的runtest的程序)

### 2014/08/04
1. globalSet更新,支持globalSet(key=value)，兼容原有的globalSet({})

### 2014/07/31
1. dev.getMem接口调整，原来返回PSS值，现在返回{'PSS':pss, 'VSS':vss, 'RSS':rss}
2. 新增airtest的图形界面，方面快速的截图和写代码
3. 图像文件名支持unicode中文，支持在多个图片文件夹里自动搜索
4. 增加globalGet函数

### 2014/07/21
1. 增加airtest自测代码
2. 修正ios中的屏幕旋转问题
3. 增加关于屏幕设置的文档

### 2014/07/17
1. 增加start,stop,clear函数
1. globalSet增加mem和cpu监控周期调整。globalSet({'monitor_interval': 5})
