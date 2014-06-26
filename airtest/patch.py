#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time

from functools import partial

def attachmethod(target):
    if isinstance(target, type):
        def decorator(func):
            setattr(target, func.__name__, func)
    else:
        def decorator(func):
            setattr(target, func.__name__, partial(func, target))
    return decorator

def fuckit(fn):
    def decorator(*argv, **kwargs):
        try:
            return fn(*argv, **kwargs)
        except Exception as e:
            argv.extend([k+'='+v for k, v in kwargs.items()])
            print 'function(%s(%s)) panic(%s). fuckit' %(fn.__name__, ' ,'.join(argv), e)
            return None
    return decorator

def record(logfile=None):
    ''' decorator for class '''
    logfile = os.getenv('PYTEST_LOGFILE', 'log/pytest.log')
    if os.path.exists(logfile):
        backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
        os.rename(logfile, backfile)
    else:
        os.makedirs(os.path.dirname(logfile))
    logfd = open(logfile, 'w')
    def wrapper(cls):
        class NewClass(cls):
            def __getattribute__(self, name):
                obj = super(NewClass, self).__getattribute__(name)
                if callable(obj):
                    if obj.__name__.startswith('_'):
                        return obj
                    print 'record:', name
                    def func_wrapper(*argv, **kwargs):
                        print >>logfd, json.dumps({'function': name, 'argv': argv, 'kwargs': kwargs})
                        logfd.flush()
                        return obj(*argv, **kwargs)
                    func_wrapper.__doc__ = obj.__doc__ # keep the doc
                    return func_wrapper
                return obj
        return NewClass
    return wrapper
