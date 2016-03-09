Airtest
=====
Python lib for **android** and **ios** app test.

## Airtest已被重构，欢迎前往新项目地址 <https://github.com/codeskyblue/AirtestX>
重构原因：

1. 代码太多，维护量巨大
2. 很多的API不合理，需要换掉，尤其是那个connect函数
3. 原有项目历史数据太大，低带宽的网速根本无法clone代码
4. 依赖太多，安装复杂

## airtest文档
在线文档 <http://netease.github.io/airtest>

作为在线文档的一个补充，有个pydoc生成的API列表可以作为参考
 <http://netease.github.io/airtest/airtest.devsuit.html>

离线文档使用方法：

	git clone https://github.com/netease/airtest && cd airtest
	gem install jekyll
	git checkout gh-pages
	jekyll serve --baseurl=''

## 如何给给该项目贡献
因为刚项目常常更新，所以可能会有一些没有测试到的bug。

可以在发现了问题后，提个issue给作者。 另外一些新的思路也可以提到issue中。

## 相关的项目
1. 实现了touch,swipe,pinch <https://github.com/netease/airinput>
2. 基于opencv的图像识别库 <https://github.com/netease/aircv>

## License
This project is under the MIT License. See the [LICENSE](LICENSE) file for the full license text.
