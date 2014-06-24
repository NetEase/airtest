#coding: utf-8
#
__all__=['android', 'image']

import image

def connect(serialno=None):
    '''
    connect to a mobile phone
    '''
    from airtest import android
    assert serialno != None
    return android.AndroidDevice(serialno=serialno)

