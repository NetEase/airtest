--- 
title: API接口列表
layout: post
category: components
permalink: /components/apilist.html
---
**为了兼容最新版的adb,请更新 androidviewclient这个python库**, pip安装这个库会有问题，需要用easy_install手动解决

	easy_install --upgrade androidviewclient

adb也同时需要更新到1.0.32

装完后，下面的代码应该是可以顺利运行的

	import airtest
	print airtest.__version__

iOS的性能监控需要额外的一个库[paramiko](http://www.paramiko.org/installing.html)。需要该功能的话，需要首先手动安装下。

### 第一步，连接设备

airtest主要由两个类组成
	
1. **Monitor**： 负责性能数据的获取
	目前monitor支持android和ios的性能获取。
	android的性能数据主要是用`adb`去查询，而ios设备需要首先要越狱，airtest通过其开放的ssh连接上设备。

	android连接方法: `uubbff`为通过`adb devices`获取到的serialno。（如果只有一个设备的话，可以简写成`android://`) 

		mtr = airtest.Monitor('android://uubbff', 'com.netease.test')

	ios的连接方法，首先需要确定手机的ip地址，如果是通过PP苹果助手打开ssh通道，地址就会是127.0.0.1

	假设应用名叫Goddness，首先需要先验证下。命令行验证下`ps -eo pid,command | grep Goddness` 是不是能匹配出来结果

		mtr = airtest.Monitor('ios://10.2.0.1', 'Goddness')

2. **Device**: 包含操作类相关的接口
	参数类似Monitor，但是只有第一个参数。

	连接android设备, 如果没有指定serialno的话，airtest还会从环境变量`AIRTEST_SERIALNO`去尝试获取

		dev = airtest.Device('android://uubbff')

	连接苹果设备。因为苹果手机的流行，兼容苹果是必须的。
	需要注意的是ios的连接靠的是appium，只能用mac去连接ios设备，这个限制有点大（Monitor类在windows上也是可以的）。
	地址是appium server的地址。一般都是127.0.0.1（这个是默认值）

		dev = airtest.Device('ios://127.0.0.1')

3. **整合类**: 把两个类的方法到一个类
	好多应用场景是为了操作和性能一起来，这里用了python的一些技巧，使得Monitor和Device这两个类的方法放到了一个对象中。

	connect的函数是这样定义的。

		def connect(addr, appname=None, device=None,
				monitor=True, interval=3.0, logfile='log/airtest.log')

	调用的例子（保持这种也是为了和过去的用法兼容，不过还是要修改一点)

	原来的 `airtest.connect('ubbff', appname='com.netease.test', device='android')`
	同时也支持 `airtest.connect('android://uubbff', 'com.netease.test')`

		app = airtest.connect('android://uubbff', 'com.netease.test', 'android', monitor=False)
		print app.cpu()
		app.click(u'start.png')

	当`appname!=None`的时候，interval和logfile这两个参数才会起作用. `monitor=True`的话，启动后,监控日志就会开始记录

		app = airtest.connect('uubbff', 'com.netease.test', 'android', 
				monitor=True, interval=2.0, logfile='log/airtest.log')
		app.safeWait(u'start.png')
	
	上面这段代码, 是每隔2s中，将性能数据记录到log/airtest.log中。直到代码运行结束

	如果不设置monitor，但是设置的appname的话是可以通过下面这两个命令，控制的
	
		app.startMonitor() # 启动监控
		app.stopMonitor() # 停止监控

### 接口文档格式

接口的说明采用如下格式

	function(arg0:type, arg1:type(default), [optional1])

我用中文翻译下

	函数名(参数1:类型, 参数2:类型(默认值), [可选参数1])

### 分类：Monitor接口 
![rotation]({{site.baseurl}}/static/img/monitor.png)
主要集中在cpu和mem的数据获取上

#### cpu()
获取应用cpu的利用率，范围`[0.0, 100.0]`

#### sys_cpu(percpu:bool(False))
只android上有。 获取系统的cpu占用率

* percpu=false的时候，返回一个float值，范围 [0, 100.0]
* percpu=true 的时候，返回一个list列表, eg `[30.0, 20.1, 40, 80.0]`

#### pid()
只ios有。返回int。也就是进程的pid

#### memory()
获取内存占用量 (单位KB). android与ios返回的数据有点区别

android的数据是

	{"PSS": 129560, "VSS": 1051236, "RSS": 170048}

ios的则是, 少了个PSS

	{"VSS": 1051236, "RSS": 170048}

#### sys_memory()
获取系统当前内存(单位KB)， ios还没有

数据返回 example

	{'TOTAL': 2048, 'FREE': 123}

#### battery()
借助了`adb shell dumpsys battery`，目前ios还没有 *0.9.14版本开始引入到android*

一个返回值的例子, 详细的介绍可以看这里<http://imsardine.simplbug.com/note/android/adb/commands/dumpsys-battery.html>

	{
		'status': 2,  // 1:unknown, 2:charging, 3:discharning, 4:notcharning, 5:full
		'scale': 100,  // 和level一起看
		'temperature': 265, // 代表26.5摄氏度
		'level': 8, // 属于电量百分比 = level / scale * 100 = 8%
		'AC powered': False,  // 交流电
		'health': 2, // 1:unknown, 2:good, 3:overheat 4:dead 5:over_voltage, 6:unspecified_failure 7:cold
		'voltage': 3757, // 当前电压 millivolts,mV 毫伏 3.737V
		'Wireless powered': False, // 这个太高端，不解释了
		'USB powered': True, // USB充电？
		'technology': 'Li-ion', // 电池类型
		'present': True // 表示电池是否在手机里
	}


### 分类：Device接口
![rotation]({{site.baseurl}}/static/img/device.png)
API比较多，如果遇到接口问题。请反馈到 <https://github.com/netease/airtest/issues>

#### globalSet(kwargs)
这个接口可以接受的参数很灵活。如

	app.globalSet(operation_mark=True)

下面列出常用的配置

	配置名			默认值			说明
	click_timeout		20.0			click函数的默认超时时间
	delay_after_click	0.5			点击完成后的等待时间
	operation_mark		False			是否在图像匹配的时候，标记找到的位置。图像存储在tmp下
	image_match_method	'auto'			可以选择的有auto,template,sift。更多的请参考 https://github.com/netease/aircv
	image_dirs		['.', 'image']	list类型。指定在那些文件夹下查找图片
	snapshot_method		'adb'			可以选择的参数有adb,screencap。一种是用framebuffer的方式截图，一种是用screencap命令行。如果一种不行就换下试试
	screen_resolution	None			下面专门有说明
	rotation		None			(暂时设置也不能用, 直到改消息去掉)int行，可选的值有0,1,2,3 可参考rotaion()这个函数的介绍

`screen_resolution`是为了能使一台手机上的截图更容易的匹配别的机器。根据两个手机的宽高比，进行相应的缩放。从而提高识别率。

	app.globalSet(screen_resolution=(1080, 1920)) # eg

#### globalSet(key:str)
获取相应的配置值

	app.globalGet(screen_resolution)

#### takeSnapshot(filename:str)
filename要求扩展名是png或者jpg

    app.takeSnapshot('snapshot.png')

#### rotation()
获取屏幕旋转方向: 基于`dumpsys input | grep SurfaceOrientation`

返回值有4个, int类型

	from airtest import proto
	proto.ROTATION_0, proto.ROTATION_90, proto.ROTATION_180, proto.ROTATION_270

![rotation]({{site.baseurl}}/static/img/rotation.png)

#### keepCapture()
图形查找时，使用上次的屏幕截图。可以用来提高脚本的运行效率。

#### releaseCapture()
关闭keepCapture

#### startApp(appname:str, activity:str)
启动app应用, activity目前是必选的。 还不支持ios

目前调用的是`adb shell am start -n package/activity`

	app.startApp('com.netease.test', '.Main')

#### stopApp(appname:str)
停止app应用

目前调用的是 `adb shell am force-stop package`

	app.stopApp('com.netease.test')

#### click(P, [timeout:float(20.0)], duration=0.1)
点击图片，或者点击坐标。图片如果没有的timeout时间内找到的话，就会抛异常了

    长按的支持：
    eg: 点击2s  click((100, 200), duration=2.0)

    app.click(P)
    # P can be
    # - filename: 'start.png'
    # - position: (100, 200)
    # - percent: (0.1, 0.02)    # equal to (width*0.1, height*0.02)

    # click-timeout(only avaliable when P is string)
    # equals to app.click(app.find('start.png', 20.0))
    app.click('start.png', 20.0) # if start.png not found in 20s, Exception will raised.

#### find(image_file:str)
获取一个图片在当前屏幕上的坐标

    (x, y) = app.find(filename)


#### findall(self, imgfile, maxcnt=None, sort=None): # sort = <None|"x"|"y">
	FIXME(ssx): 该接口不太稳定，beta测试中

    findall('start.png', maxcnt=2)
    findall('start.png', maxcnt=2, sort='x') # sort ordered by x row

#### sleep(secs:float)
等价于time中的sleep函数, 如果开启日志记录的话，会有日志记录到airtest.log文件中。

    app.sleep(2.0)  # sleep 2.0s

#### log(tag_name, object)
记录信息到日志文件中。 object可以是最终会用`json.dumps(object)`处理

    app.log('myTag', {'name': 'tt'})

记录到文件中将是

    {"timestamp": 13002849, "tag": "myTag", "data": {"name": "tt"}}

#### wait(image_file:str, [timeout:float])
返回找到的坐标

一直等到图片的出现，函数才结束。图片找不到会跑出`RuntimeError`的异常。
timeout现在默认是20（可能以后会改）.

	position = app.wait('end.png', 20.0)

#### safeWait(filename, [seconds]) # like wait, but donot raise RuntimeError
跟wait差不多。只不过找不到图片，不会抛异常而是会返回None

    pt = app.safeWait(filename)
	if pt:
	    print 'Position:', pt
	else:
	    print 'picture not found'

#### exists(...) # judge if image exists

    app.exists('apple.png')
    # @return (True|False)
    # just exactly call wait


#### shape()
这里的宽度始终小于高度

    (w, h) = app.shape()

#### drag(P1, P2, [duration:float(2.0)])

`P1,P2`可以是坐标，可以是文件名。 举几个例子

	app.drag((100, 200), (100, 800), duration=2.0)
	app.drag('start.png', 'end.png')
	app.drag((100, 200), 'end.png')

如果坐标系的参数小于1的话。坐标的x,y会自动乘以宽高。
根据屏幕旋转方向，宽高会有所不同

	app.drag((0.2, 0.1), (0.2, 0.9))

#### type(msg)
如果msg中有`\n`的话，会自动替换成执行`ENTER`命令。

    app.type('www.baidu.com\n')


#### keyevent(event:str)
android的keyevent时间。 使用`adb shell input keyevent`实现

可以填的参数很多，功能也非常强大。可以参考官方的[keyevent列表](http://developer.android.com/reference/android/view/KeyEvent.html)

举一些常用的例子

    app.keyevent('BACK') # 回退键
    app.keyevent('MENU') # 菜单
	app.keyevent('ENTER') # 确认
	app.keyevent('SEARCH') # 搜索
	app.keyevent('VOLUME_UP') # 音量+
	app.keyevent('VOLUME_DOWN') # 音量-
	app.keyevent('POWER') # 电源键

