Change Log
=================

### 2014/07/17
1. 增加start,stop,clear函数
1. globalSet增加mem和cpu监控周期调整。globalSet({'monitor_interval': 5})

### 2014/07/21
1. 增加airtest自测代码
2. 修正ios中的屏幕旋转问题
3. 增加关于屏幕设置的文档

### 2014/07/31
1. dev.getMem接口调整，原来返回PSS值，现在返回{'PSS':pss, 'VSS':vss, 'RSS':rss}
2. 新增airtest的图形界面，方面快速的截图和写代码
3. 图像文件名支持unicode中文，支持在多个图片文件夹里自动搜索
4. 增加globalGet函数

### 2014/08/04
1. globalSet更新,支持globalSet(key=value)，兼容原有的globalSet({})

### 2014/08/12
1. 增加image_match_method配置项，可以手动选择图形匹配算法
2. 环境变量AIRTEST_DEVNO改名为AIRTEST_PHONENO(影响范围，使用air.test命令行的runtest的程序)

### 2014/08/14
1. 增加app.monitor变量， 可以通过app.monitor.start() 启动监控和通过app.monitor.stop()停止监控
2. 增加fps的支持

### 2014/08/20
1. 新增airtoolbox工具（该工具可以运行在手机上，采集手机的内存，网卡信息，模拟长按的操作）
2. 完成air.test gen命令

### 2014/08/27
1. 支持python -mairtest 等价于 命令行的air.test
2. log2html生成的文件支持点击放大的效果。
3. 修复air.test gen命令，对于某些apk，不生效的问题。

### 2014/08/29
1. 输入法支持中文及特殊字符
