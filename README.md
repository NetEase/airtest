airtest
=====
this is python lib for airtest

AirTest PoPo Discuss Group: **1275211**

成功也好，失败也好，或者只想吐槽，欢迎直接反馈到群里。

关于屏幕旋转一直也没有一个很好的解决方案，现在的方法需要手工去设置旋转方向。

具体需要参考这篇文章 [airtest中的屏幕旋转如何设置](http://doc.mt.nie.netease.com/doku.php?id=airtest-screen-rotate)

[![Build Status](http://jenkins.mt.nie.netease.com/job/airtest_selftest/badge/icon)](http://jenkins.mt.nie.netease.com/job/airtest_selftest/)

### For windows: 
Windows need python2.7 32bit.

Download Resouce from here: <http://pan.baidu.com/s/1eQFyg4E> Password: `dt77`.
Install according to the number one by one.

Last step: Copy `cv2.pyd` to `python/lib/site-packages`

install pythonlib: **androidviewclient**
```
pip install -U -i http://mt.nie.netease.com:3141/simple/ androidviewclient
```

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>
1. numpy
1. opencv
1. pillow
    * Windows: download pillow from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>
    * Linux: A little complicated. It's better to install from source.

### For ios test (only on Mac OS)
Auto install airtest by run: 
```
bash -c "$(curl -s http://git.mt.nie.netease.com/hzsunshx/airtest/raw/master/scripts/mac_install.sh)"
```

Or manual

1. brew: <http://brew.sh/>
1. python: `brew install python`
1. appium: `brew install node && npm install -g appium`
1. opencv: `brew tap homebrew/science && brew install opencv` 
1. pillow: `brew tap Homebrew/python && brew install pillow`
1. appclient: `pip install Appium-Python-Client`

## Last but import: install airtest
install using pip(stable).
```
pip install -U -i http://mt.nie.netease.com:3141/simple/ airtest
```

## Check if install OK
for android

Run [flappybird example program](example/flappybird)

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
phoneno = os.getenv('AIRTEST_PHONENO') or 'xxxxx888882111' # phone number
appname = os.getenv('AIRTEST_APPNAME') or 'com.netease.rz' # the application name
deviceType = 'android' # can be windows or ios

# connect to your android devices
app = airtest.connect(phoneno, appname=appname, device=deviceType)
```

click(...) # click by image file
```
app.click(P)
# P can be
# - filename: 'start.png'
# - position: (100, 200)
# - percent: (0.1, 0.02)    # equal to (width*0.1, height*0.02)
```

find(...) # find a image position located in screen
```
(x, y) = app.find(filename)
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

drap(...) # drag one place to and onother place
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

### about airtest settting
phone has 4 directions: `UP,DOWN,LEFT,RIGHT`

change rotation through
```
app.globalSet({'rotation': 'RIGHT'})
```

change image recognize sensitivity
```
# threshold range [0, 1), if set to 1, then app can't recognize anything
app.globalSet({'threshold': 0.3}) 
```

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

airtest develop version(not stable)
```
pip install -U git+http://git.mt.nie.netease.com/hzsunshx/airtest.git
```


## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
