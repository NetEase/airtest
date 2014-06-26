pyairtest
=====
this is python lib for airtest

## install
install use pip.
```
pip install -U git+https://github.com/blackair/airtest.git
```
`androidviewclient` is not working well with pip, you have to install it with `easy_install`.

`pillow` is also needed.

* Mac: run `brew install pillow`
* Windows: download pillow from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>
* Linux: A little complicated. It's better to install from source.

the command `adb` is should be found in $PATH

after finish install. you can use import airtest. and can run `air.test` and `snapshot`.

## write test case
after installed successfully. you can import like
```python
import airtest
serialno = 'xxxxx888882111' # get it by call: adb devices
app = airtest.connect(serialno)
if app.exists('apple.png'):
    app.click('buy.png')
app.wait('finish.png')
app.click('confirm.png')
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

## good luck
author: hzsunshx
email: hzsunshx@corp.netease.com

## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
