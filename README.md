Airtest
=====
Python lib for Mobile phone app test.


网易内部Popo交流群: **1275211** *

在线文档 <http://netease.github.io/airtest>

离线文档使用方法：

	git clone http://git.mt.nie.netease.com/hzsunshx/airtest && cd airtest
	gem install jekyll
	git checkout gh-pages
	jekyll serve --baseurl=''


关于**屏幕旋转**一直也没有一个很好的解决方案，现在的方法需要手工去设置旋转方向。
具体需要参考这篇文章 [airtest中的屏幕旋转如何设置](http://doc.mt.nie.netease.com/doku.php?id=airtest-screen-rotate)

目前的wiki在, 很多问题可以再上面找到答案： <http://doc.mt.nie.netease.com/doku.php?id=airtest>

## Development document
AndroidKeyMap: <http://developer.android.com/reference/android/view/KeyEvent.html>

used by call, eg
```
app.keyevent("HOME")
```


## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
