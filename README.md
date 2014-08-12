airtest
=====
this is python lib for airtest

AirTest PoPo Discuss Group: **1275211**

成功也好，失败也好，或者只想吐槽，欢迎直接反馈到群里。

关于**屏幕旋转**一直也没有一个很好的解决方案，现在的方法需要手工去设置旋转方向。
具体需要参考这篇文章 [airtest中的屏幕旋转如何设置](http://doc.mt.nie.netease.com/doku.php?id=airtest-screen-rotate)

airtest目前的wiki在, 很多问题可以再上面找到答案： <http://doc.mt.nie.netease.com/doku.php?id=airtest>

airtest具体的API依然维护这个README上面

[![Build Status](http://jenkins.mt.nie.netease.com/job/airtest_selftest/badge/icon)](http://jenkins.mt.nie.netease.com/job/airtest_selftest/)

## INSTALL
[Click HERE](INSTALL.md)

## Check if install OK
for android

Run [flappybird example program](http://git.mt.nie.netease.com/hzsunshx/flappybird)

download test code through:
```
git clone http://git.mt.nie.netease.com/hzsunshx/flappybird
```

## run test case
### step1: prepare air.json file.
the command tool `air.test` is installed. If everything goes fine.

config file `air.json` is needed by `air.test`. here is an example
```json
{
  "cmd": "python main.py",
  "android": {
    "apk_url": "http://10.246.13.110:10001/demo-release-signed.apk",
    "package": "com.netease.xxx",
    "activity": "main.activity"
  }
}
```

### step2: prepare the test code
main.py code example
```
import airtest

phoneno = os.getenv('AIRTEST_PHONENO')
appname = os.getenv('AIRTEST_APPNAME')
device = os.getenv('DEVICE') or 'android'

app = airtest.connect(phoneno, appname=appname, device=device)
(width, height) = app.shape() # get device size
app.click('start.png') # locate start.png position and touch it
```

So where is `start.png` image file from.

take screen snapshot by run: `air.test snapshot`, screen will save to `screen.png`

cut the image part from it.

### step3: run test code
1. connect you device. if you use android, `adb devices` should see a devices
2. install app. `air.test install`
3. runtest. `air.test runtest`
4. generate log, and show html in Chrome. `air.test log2html --listen --port=8888 report`
5. uninstall app. `air.test uninstall`

open browser, input `127.0.0.1:8888`. You should see html report now.

## API Reference
after installed successfully. you can import like
```
# import python lib
import airtest
```

step1 connect device
```
# get serialno by call: adb devices
phoneno = os.getenv('AIRTEST_PHONENO') or 'xxxxx888882111' # bundleid or serialno
appname = os.getenv('AIRTEST_APPNAME') or 'com.netease.rz' # app name
deviceType = 'android' # can be windows or ios

# connect to your android devices
# default value: device='android', monitor=True
app = airtest.connect(phoneno, appname=appname, device=deviceType, monitor=True)
```

takeSnapshot(filename) # filename show with extention (.jpg or .png)
```
app.takeSnapshot('snapshot.png')
```

click(P, [seconds], eventType=airtest.EV_DOWN_AND_UP) # click by image file
```
app.click(P)
# P can be
# - filename: 'start.png'
# - position: (100, 200)
# - percent: (0.1, 0.02)    # equal to (width*0.1, height*0.02)

# click-timeout(only avaliable when P is string)
# equals to app.click(app.find('start.png', 20.0))
app.click('start.png', 20.0) # if start.png not found in 20s, Exception will raised.

# long press (this is an experimental function, report problem if something goes wrong)
app.click(P, eventType=airtest.EV_DOWN)
time.sleep(1.0) # press 1s
app.click(P, eventType=airtest.EV_UP)
```

find(...) # find a image position located in screen
```
(x, y) = app.find(filename)
```

findAll(self, imgfile, maxcnt=None, sort=None): # sort = <None|"x"|"y">
```
findAll('start.png', maxcnt=2)
findAll('start.png', maxcnt=2, sort='x') # sort ordered by x row
```

wait(...) # wait until image shows
```
app.wait(filename, [seconds])
# filename is the image name
# seconds is the longest time waited.
# @return position images find, or Raise RuntimeError
# this is called find(..) to get images position
```

exists(...) # judge if image exists
```
app.exists('apple.png')
# @return (True|False)
# just exactly call wait
```

drag(...) # drag one place to and onother place
```
app.drag(fromP, toP)
# fromP, toP: like click param, can be filename or position
```

shape() # get screen size(width and height)
```
(w, h) = app.shape()
# return width and height
```

```
# example of drag from left to right
(x1, y1), (x2, y2) = (w*0.2, h*0.5), (w*0.8, h*0.5)
app.drag((x1,y1), (x2,y2))
```

type(...) # type text
```
app.type('www.baidu.com\n') # type text and call keyevnet ENTER
```

keyevent(not recommemd to use now)
```
# back and menu(only for android)
app.keyevent('BACK')
app.keyevent('MENU')
```

### airtest settting
Mobile phone has 4 directions: `UP,DOWN,LEFT,RIGHT`.
Change rotation through. more info view: <http://doc.mt.nie.netease.com/doku.php?id=airtest-screen-rotate>
```
app.globalSet({'rotation': 'RIGHT'})
```

Change image recognize sensitivity
```
# threshold range [0, 1)
# the bigger the accurate. If set to 1, then app can't recognize anything
app.globalSet({'threshold': 0.3}) 
```

关于更详细的配置，请参考: <http://doc.mt.nie.netease.com/doku.php?id=airtest#设置接口globalset和globalget>

## 更新日志
[CHANGELOG](CHANGELOG.md)

## Team

	孙圣翔 hzsunshx@corp.netease.com
	- 项目管理员
	
	刘欣 gzliuxin@corp.netease.com
	- IOS后端接口开发者

	熊博 gzxiongbo@corp.netease.com
	- IOS后端接口开发者

	贾强槐 hzjiaqianghuai@corp.netease.com
	- 图像识别

## development document
AndroidKeyMap: <http://developer.android.com/reference/android/view/KeyEvent.html>

used by call, eg
```
app.keyevent("HOME")
```


## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
