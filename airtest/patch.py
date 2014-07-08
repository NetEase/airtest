#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import threading

from functools import partial

from airtest import base
from airtest import jsonlog

def attachmethod(target):
    if isinstance(target, type):
        def decorator(func):
            setattr(target, func.__name__, func)
    else:
        def decorator(func):
            setattr(target, func.__name__, partial(func, target))
    return decorator

def fuckit(fn):
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            args.extend([k+'='+v for k, v in kwargs.items()])
            print 'function(%s(%s)) panic(%s). fuckit' %(fn.__name__, ' ,'.join(args), e)
            return None
    return decorator

def record(logfile=None):
    ''' decorator for class '''
    if os.path.exists(logfile):
        backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
        os.rename(logfile, backfile)
    else:
        base.makedirs(base.dirname(logfile))

    jlog = jsonlog.JSONLog(logfile)
    #logfd = open(logfile, 'w')
    def wrapper(cls):
        class NewClass(cls):
            def __getattribute__(self, name):
                obj = super(NewClass, self).__getattribute__(name)
                if callable(obj):
                    if obj.__name__.startswith('_'):
                        return obj
                    print 'record:', name
                    def func_wrapper(*args, **kwargs):
                        jlog.writeline({'timestamp': int(time.time()), 'function': name, 'args': args, 'kwargs': kwargs})
                        return obj(*args, **kwargs)

                        #print >>logfd, json.dumps({'timestamp': int(time.time()), {'function': name, 'args': args, 'kwargs': kwargs})
                        #logfd.flush()
                    func_wrapper.__doc__ = obj.__doc__ # keep the doc
                    return func_wrapper
                return obj
        return NewClass
    return wrapper

def go(fn):
    def decorator(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
        return t
    return decorator

# test code
if __name__ == '__main__':
    @go
    def say_hello(sleep=0.3, message='hello world'):
        time.sleep(sleep)
        print message
    t1 = say_hello(0.1)
    t2 = say_hello(0.5, 'this message should not showed')
    t1.join()
