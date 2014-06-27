#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
simple json log
'''
import json
import threading

class Lock(object):
    def __init__(self, tlock):
        self.lock = tlock
    
    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, *args):
        self.lock.release()

class JSONLog(object):
    def __init__(self, filename=None):
        self.filename = filename
        self._fd = None
        self._lock = threading.Lock()

    def writeline(self, d, *args):
        '''
        @param d (dict or string): content needed write to file
        '''
        with Lock(self._lock) as _:
            if not self._fd:
                assert self.filename != None
                self._fd = open(self.filename, 'a')
            if isinstance(d, dict):
                outline = json.dumps(d)
            else:
                outline = str(d) % args
            self._fd.write(outline.rstrip() + '\n')
            self._fd.flush()

if __name__ == '__main__':
    log = JSONLog('test.log')
    log.writeline('hello')
    log.writeline({'hello': 'world'})
