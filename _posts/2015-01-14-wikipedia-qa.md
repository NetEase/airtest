--- 
title: 常见问题
layout: post
category: wikipedia
permalink: /wikipedia/question-answer.html
---

1. 问题: `app.type`不能使用

	可能原因： Android手机上airtest使用了一个自带的输入法adb-keyboard, 请确认安装并没有禁用它。
	可以再PYTHONLIB目录下的site-packages/airtest/binfiles下面找到这个文件
