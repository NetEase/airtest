--- 
title: 快速入门
layout: post
category: overview
permalink: /overview/quick_start.html
---

下面将用一个例子说明一下怎么使用Airtest.




1. 按照[安装文档][installing]上的说明，一步步的完成安装

2. 下载[样例代码](http://git.mt.nie.netease.com/hzsunshx/flappybird): *没有git，[点此下载](ftp://mt.nie.netease.com/airtest-win-res/Git-1.9.4-preview20140815.exe)*

		git clone http://git.mt.nie.netease.com/hzsunshx/flappybird

3. ...


The important lesson here is that `nsq_to_file` (the client) is not explicitly told where the `test`
topic is produced, it retrieves this information from `nsqlookupd` and, despite the timing of the
connection, no messages are lost.

[installing]: {{ site.baseurl }}/deployment/installing.html
