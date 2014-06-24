pyairtest
=====
this is python lib for airtest

## install
install use pip.
```
pip install -U git+http://git.mt.nie.netease.com/hzsunshx/pyairtest.git
```

you have to install `androidviewclient` and `pillow` by easy\_install.
```sh
easy_install androidviewclient
easy_install pillow
```
It is very for windows users for you can find packages from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>

## write test case
after installed successfully. you can import like
```python
import airtest
app = airtest.connect('xx8123a')
app.click('start.png')
```

## run test case
the command tool `air.test` is also installed when run setup.py.

config file `air.json` is needed by `air.test`. here is an example
```json
{
  "cmd": "python main.py -s ${SERIALNO}",
  "android": {
    "apk_url": "http://10.246.13.110:10001/demo-release-signed.apk",
    "package": "com.netease.h15",
    "activity": "org.cocos2dx.lua.AppActivity"
  }
}
```

command will be called by `air.test` after successfully installed apk.
```sh
bash -c "python main.py -s ${SERIALNO}"
```

## good luck
author: hzsunshx
email: hzsunshx@corp.netease.com
