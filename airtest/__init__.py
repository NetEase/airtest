#coding: utf-8
#
__all__=['android', 'image', 'base']

import subprocess

def connect(serialno=None):
    '''
    connect to a mobile phone
    '''
    from airtest import android
    assert serialno != None
    return android.AndroidDevice(serialno=serialno)

def getDevices():
    ''' return devices list '''
    subprocess.call(['adb', 'start-server'])
    output = subprocess.check_output(['adb', 'devices'])
    result = []
    for line in output.splitlines()[1:]:
        ss = line.strip().split()
        if len(ss) == 2:
            (serialno, state) = ss
            result.append((serialno, state))
    return result

#if __name__ == '__main__':
    #print getDevices()

