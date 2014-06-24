#!/usr/bin/env python
# coding: utf-8
'''
grabe screen picture from android device
Usage:
    snapshot [-o FILE] [-s serialno]

Options:
    -o FILE      Save snapshot to a file [default: screen.png]
    -s serialno  specify devices
'''

import docopt
from com.dtmilano.android.viewclient import ViewClient 
print 'good'

def main():
    print 'connect to device'
    arguments = docopt.docopt(__doc__)
    serialno = arguments.get('-s')
    saveto = arguments.get('-o')
    c, _ = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
    print 'brand:', c.getProperty('ro.product.brand')
    print 'saving snapshot to "%s"'%(saveto)
    s = c.takeSnapshot()
    s.save(saveto)

if __name__ == '__main__':
    main()
