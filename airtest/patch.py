#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time

def record(cls):
    ''' decorator for class '''
    logfile = os.getenv('PYTEST_LOGFILE', 'log/pytest.log')
    if os.path.exists(logfile):
        backfile = logfile+'.'+time.strftime('%Y%m%d%H%M%S')
        os.rename(logfile, backfile)
    else:
        os.makedirs(os.path.dirname(logfile))
    logfd = open(logfile, 'w')

    class NewClass(cls):
        def __getattribute__(self, name):
            # print >>logfd, json.dumps({'action': name})
            obj = super(NewClass, self).__getattribute__(name)
            if callable(obj):
                if obj.__name__.startswith('_'):
                    return obj
                print 'record:', name
                def func_wrapper(*argv, **kwargs):
                    print >>logfd, json.dumps({'action': name, 'argv': argv, 'kwargs': kwargs})
                    logfd.flush()
                    return obj(*argv, **kwargs)
                return func_wrapper
            return obj
    return NewClass