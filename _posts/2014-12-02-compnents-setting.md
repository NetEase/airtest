--- 
title: 参数设置
layout: post
category: components
permalink: /components/setting.html
---

#### 设置接口globalSet和globalGet

使用方法举例

    app.globalSet(image_dirs=['.', 'image'])

通过globalGet可以拿到这些默认的配置

    app.globalGet('image_dirs') # 期望拿到['.', 'image']

目前有的一些参数是：系统默认的

    image_exts: ['.jpg', '.png'],
    image_dirs: ['.', 'image'],
    threshold: 0.3,  #图像识别的阈值
    rotation: None, # 自动判断的，最好还是手工配置下，4个可选值 UP,LEFT,RIGHT,DOWN
    monitor_interval: 5， #采集mem和cpu的周期
    
    click_timeout: 20.0, # 
    如果click一个图标的时候，在20s内，依然没有查找到，则抛出异常

    delay_after_click': 0.5, # 完成点击后的等待时间
    image_match_method: 'auto', # 可以选择 template（模板匹配） 或者 auto（混合匹配）， sift（特征点匹配-还没弄好）
    threshold: 0.3， # 模板匹配涉及到的阈值， template 建议0.8, auto建议0.3， sift还没想好

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

    app.globalSet(image_match_method='template', threshold=0.8)

#### 图片的搜索路径的设置
系统默认的设置时这样的

    app.globalSet(image_exts=['.jpg', '.png'], image_dirs=['.', 'image'])

还有一个目录是image_pre_search_dirs, 搜索时会优先于image_dirs, 这个值的参数是根据手机型号自动生成的（比如手机android，分辨率800*1000)

那么通过

    app.globalGet('image_pre_search_dirs')

拿到的结果，就会使 ['image-800_1000', 'image-android']

自动搜索图片路径的好处就是，不用再代码中把图片的全路径和扩展名写出来了，比如我们可以这样写

    app.click('start')
    app.click(u'开始') # 中文名前面需要加u

目录结构

    .
    |-- image
    |   `-- start.png
    `-- image-800_1000
        `-- 开始.png