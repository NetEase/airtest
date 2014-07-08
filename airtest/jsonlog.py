#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
simple json log
'''
import json
import threading
import time

from airtest import base

class Lock(object):
    def __init__(self, tlock):
        self.lock = tlock
    
    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, *args):
        self.lock.release()

_LOGS={}

class JSONLog(object):
    def __init__(self, filename):
        base.makedirs(base.dirname(filename))

        self._filename = filename
        self._fd = _LOGS.get(filename) or open(filename, 'a')
        self._lock = threading.Lock()

    def writeline(self, d, *args):
        '''
        @param d (dict or string): content needed write to file
        @param args(array): only when d is string, support writeline('hello %s', 'world')
        '''
        with Lock(self._lock) as _:
            if isinstance(d, dict):
                d.update({'timestamp': int(time.time())})
                outline = json.dumps(d)
            else:
                outline = str(d) % args
            self._fd.write(outline.rstrip() + '\n')
            self._fd.flush()

if __name__ == '__main__':
    log = JSONLog('test.log')
    log.writeline('hello')
    log.writeline({'hello': 'world'})
