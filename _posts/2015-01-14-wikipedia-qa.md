--- 
title: 常见问题
layout: post
category: wikipedia
permalink: /wikipedia/question-answer.html
---

1. 问题: `app.type`不能使用

	可能原因： Android手机上airtest使用了一个自带的输入法adb-keyboard, 请确认安装并没有禁用它。
	可以再PYTHONLIB目录下的site-packages/airtest/binfiles下面找到这个文件

2. 出现连接失败

	如果是windows的话。打开进程管理器看看有没有`AndroidServer.exe`这个进程。然后`adb start-server`启动下就好了。
