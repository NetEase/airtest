pyairtest
=====
this is python lib for airtest

## install
install from source:
```
python setup.py install
```

## write test case
after installed successfully. you can import like
```python
import airtest
app = airtest.connect('xx8123a')
app.click('start.png')
```

## run test case
the command tool `air.test` is also installed when run setup.py.

run below command for more help.
```sh
air.test -h
```

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

cmd will be called by
```sh
bash -c "python main.py -s ${SERIALNO}"
```

## good luck
author: hzsunshx
email: hzsunshx@corp.netease.com
