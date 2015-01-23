--- 
title: 使用技巧
layout: post
category: components
permalink: /components/snippets.html
---

#### 使用已有的图片进行图片查找
如果已经有图片 比如 `saved.png`

可以通过下面的代码

	app.globalSet(snapshot_file='saved.png')
	app.keepCapture() # 不重新截图

查找的速度开始变得飞快

	print app.find('ok.png')

重新开启每次操作截图

	app.releaseCapture() # 使可以重新截图

#### 截图方法设置（仅适用于Android）
    app.globalSet(snapshot_method='adb') # 默认

默认的方法，推荐使用，但是常常会遇到有些手机截图出现问题的情况，这个时候可以换成命令行 screencap截图的方法

    app.globalSet(snapshot_method='screencap')

#### 分辨率设置

设置图像采集的屏幕分辨率（eg: 分辨率是1080×1920) , 该参数会极大的改善代码迁移到其他手机上上时的识别率。

    app.globalSet(screen_resolution=(1080, 1920))

#### 图片匹配算法的选择
选择混合算法匹配（大概1s左右，可以适应屏幕尺度的变化）

    app.globalSet(image_match_method='auto'， threshold=0.3)

选择模板匹配（大概0.1s左右，不能适应屏幕尺度的变化，尺度不变时，准确度很高）

    app.globalSet(image_match_method='template', threshold=0.7)
