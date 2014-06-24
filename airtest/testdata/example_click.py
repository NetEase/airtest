# coding: utf-8
#
'''
sample test program
@author: hzsunshx
@date: 2014/06/20
'''

import air

def test_playMusic():
    d = air.AndroidDevice()#'10.242.74.241:5555')
    d.setImageDir('testdata')
    d.click('qqmusic.png')
    d.click('mylove.png', delay=1)
    d.click('danger.png')

if __name__ == '__main__':
    test_playMusic()

    #d = AndroidDevice()#'4d005f1f9df03107')
    #d.tag('touch start game')
    #d.takeSnapshot('oppo.png')

    #d.startActivity('com.netease.h15/XyqMobile')
    # use image api to get position
    #pos = _image_locate('oppo.png', 'finish.png')
    # touch position
    #d.touch(pos[0], pos[1])
    #time.sleep(0.5)
    #d.takeSnapshot().save('clicked.png', format='PNG')
