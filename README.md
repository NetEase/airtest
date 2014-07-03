pyairtest
=====
this is python lib for airtest

## install
install using pip.
```
pip install -U airtest
```

Other python lib required which may need installing by yourself.

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>
1. AndroidViewClient: `easy_install --upgrade androidviewclient`
1. opencv
1. pillow
    * Windows: download pillow from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>
    * Linux: A little complicated. It's better to install from source.

### For ios test (only on Mac OS)
1. brew: <http://brew.sh/>
1. appium: `brew install node; npm install -g appium`
1. Appium-Python-Client: `pip install Appium-Python-Client`
1. opencv: `brew tap homebrew/science; brew install opencv` 
1. pillow: `brew install pillow`

For windows: some resources can be found here:
Link: <http://pan.baidu.com/s/1eQFyg4E> Password: `dt77`

## write test case
after installed successfully. you can import like
```python
# import python lib
import airtest

# get serialno by call: adb devices
serialno = 'xxxxx888882111'

# connect to your android devices
app = airtest.connect(serialno)

# click by image file
app.click('confirm.png')

# wait until image shows
app.wait('finish.png')

# judge if image exists
app.exists('apple.png')

# drag one place to and onother place
app.drag('apple.png', 'plate.png')

# get screen size(width and height)
(w, h) = app.shape()

# drag by position
(x1, y1), (x2, y2) = (w*0.2, h*0.5), (w*0.8, h*0.5)
app.drag((x1,y1), (x2,y2))

# type text
app.type('www.baidu.com\n') # type text and call keyevnet ENTER

# press home
app.home()

# back and menu(only for android)
app.keyevent('BACK')
app.keyevent('MENU')

# not finished below
# get image position(TODO)
(x, y) = app.find('apple.png')
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

## good luck
author: hzsunshx
email: hzsunshx@corp.netease.com

## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
