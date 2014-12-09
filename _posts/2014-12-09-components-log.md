--- 
title: 日志说明
layout: post
category: components
permalink: /components/logformat.html
---

运行airtest的时候，会自动生成日志

日志中，会包含有cpu信息，内存，还有操作信息。 

如果希望日志中保存内存还有CPU信息的话，需要在`airtest.connect(monitor=True, ...)` 指定monitor为True

logfile也可以指定

    airtest.connect(logfile='log/airtest.log', ...)

默认的log在`log/airtest.log`, 日志的格式每行一个json的dict。dict包含3个部分

timestamp, tag, data

举例如下

    {"timestamp": 1417768463, "tag": "func", "data": {"args": [[344, 857]], "name": "click", "kwargs": {}}}

    {"timestamp": 1417768466, "tag": "cpu", "data": {"ncpu": 4, "total": 29.0}}

    {"timestamp": 1417768465, "tag": "memory", "data": {"PSS": 163585, "VSS": 1122184, "RSS": 214432}}

    {"timestamp": 1417768462, "tag": "snapshot", "data": {"filename": "tmp\\screen-141205163415-eifh.png"}}