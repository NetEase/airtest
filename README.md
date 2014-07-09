airtest
=====
this is python lib for airtest

AirTest PoPo Discuss Group: **1275211**

## install
install using pip.
```
pip install -U git+http://git.mt.nie.netease.com/hzsunshx/airtest.git
```

Other python lib required which may need installing by yourself.

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>
1. AndroidViewClient: `easy_install --upgrade androidviewclient`
1. numpy
1. opencv
1. pillow
    * Windows: download pillow from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>
    * Linux: A little complicated. It's better to install from source.

### For ios test (only on Mac OS)
1. brew: <http://brew.sh/>
1. appium: `brew install node; npm install -g appium`
1. Appium-Python-Client: `pip install Appium-Python-Client`
1. opencv: `brew tap homebrew/science; brew install opencv` 
1. pillow: `brew tap Homebrew/python; brew install pillow`
1. add python environment: `echo 'export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages' >> ~/.bash_profile`

### For windows: 
some resources can be found here:
Link: <http://pan.baidu.com/s/1eQFyg4E> Password: `dt77`

**and python should be 32bit**

## Check if install OK
for android

Run [example program](example/flappybird)

## How to use
after installed successfully. you can import like
```
# import python lib
import airtest
```

step1 connect device
```
# get serialno by call: adb devices
serialno = 'xxxxx888882111'
deviceType = 'android' # can be windows or ios

# connect to your android devices
app = airtest.connect(serialno, device=deviceType)
```

click(...) # click by image file
```
app.click(P)
# P can be
# - filename: 'start.png'
# - position: (100, 200)
```

clickOnAppear(...)
```
app.clickOnAppear(filename, [seconds])
# eg: app.clickOnAppear('image1.png', 10)
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
# press home
app.home()

# back and menu(only for android)
app.keyevent('BACK')
app.keyevent('MENU')
```

## run test case
the command tool `air.test` is also installed when run setup.py.

config file `air.json` is needed by `air.test`. here is an example
```json
{
  "cmd": "python main.py -s ${SERIALNO}",
  "android": {
    "apk_url": "http://10.246.13.110:10001/demo-release-signed.apk",
    "package": "com.netease.xxx",
    "activity": "main.activity"
  }
}
```

command will be called by `air.test` after successfully installed apk.
```sh
bash -c "python main.py -s ${SERIALNO}"
```

* take screen snapshot by run: `air.test snapshot`
* run test by run: `air.test runtest`

## about phone rotation
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
app.press("HOME")
```

## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
