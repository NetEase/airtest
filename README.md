airtest
=====
this is python lib for airtest

AirTest PoPo Discuss Group: **1275211**

成功也好，失败也好，或者只想吐槽，欢迎直接反馈到群里。

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

Run [flappybird example program](example/flappybird)

## check the API reference
[API ALL HERE](API.md)

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
