INSTALL
==================

### For windows: 
Windows need python2.7 32bit. Remember 32bit. not 64.

Download Resouce from here: <http://pan.baidu.com/s/1eQFyg4E> Password: `dt77`.
Install according to the number one by one.

install pythonlib: **androidviewclient**
```
pip install -U -i http://mt.nie.netease.com:3141/simple/ androidviewclient
```

install pythonlib: **airtest**, (Want update?, run this command again)
```
pip install -U -i http://mt.nie.netease.com:3141/simple/ airtest
```

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>
1. numpy
1. opencv
1. pillow
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

#### Dangerous: You should known what you are doing.
airtest develop version(not stable)
```
pip install -U git+http://git.mt.nie.netease.com/hzsunshx/airtest.git
```