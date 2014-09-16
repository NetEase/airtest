INSTALL
==================

### For windows: 
Windows need python2.7 32bit. Remember 32bit. not 64.

Download Resouce from here: <http://pan.baidu.com/s/1eQFyg4E> Password: `dt77`.
Install according to the number one by one.

install pythonlib: **androidviewclient**
```
easy_install androidviewclient
```

install pythonlib: **airtest**, (Want update?, run this command again)
```
pip install -U -i http://mt.nie.netease.com:3141/simple/ airtest
```

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
1. androidviewclient: `easy_install androidviewclient`

If meet error when run `python -m -c "import cv2"`, follow this may resolve.
```
brew uninstall opencv
brew install python
brew link python
brew install opencv
```

### For android test (on any platform)
1. adb: <http://developer.android.com/tools/help/adb.html>

Android上已经支持特殊字符的输入，需要提前安装输入法软件。感谢开源项目<https://github.com/senzhk/ADBKeyBoard>
The input method need to install into mobile phone. download through <http://mt.nie.netease.com/files/airtest-android-res/adb-keyboard.apk>
or use Qcode ![qcode](http://mt.nie.netease.com/files/airtest-android-res/adb-keyboard.png)


#### Below is only for developers: You should known what you are doing.
airtest develop version(not stable)
First install git for windows. [下载](ftp://mt.nie.netease.com/airtest-win-res/Git-1.9.4-preview20140815.exe), 记住勾选添加到PATH变量
```
pip install -U git+http://git.mt.nie.netease.com/hzsunshx/airtest.git
```
