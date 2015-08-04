### 介绍

**Airtest**主要应用在手机程序的自动测试和性能采集上面。

它并不是一个什么框架，而是一个python包。这样的设计可以使其非常灵活，不用担心受限于框架的各种框框。

#### Sample

    import airtest

    def main():
        app = airtest.connect()
        app.click('Start.png') # 点击开始图片
        app.click('Next.png')  # 点击下一步
        app.sleep(2.0)
        app.takeSnapshot('snap-start.png') # 保存截图

    main()


[代码地址](https://github.com/netease/airtest) |
[问题反馈](https://github.com/NetEase/airtest/issues) |
[主要维护人员](mailto:codeskyblue@gmail.com)

Popo交流群: **1275211**

点击查看 [快速入门](overview/quick_start.html)
