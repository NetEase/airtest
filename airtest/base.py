#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

def dirname(name):
    if os.path.isabs(name):
        return os.path.dirname(name)
    return os.path.dirname(os.path.abspath(name))

def exec_cmd(*cmds, **kwargs):
    '''
    @arguments env=None, timeout=3
    may raise Error
    '''
    env = os.environ.copy()
    env.update(kwargs.get('env', {}))
    timeout = kwargs.get('timeout', 120)
    try:
        import sh
        print 'RUN(timeout=%ds):'%(timeout), ' '.join(cmds)
        c = sh.Command(cmds[0])
        r = c(*cmds[1:], _err_to_out=True, _out=sys.stdout, _env=env, _timeout=timeout)
    except ImportError:
        r = subprocess.Popen(cmds, stdout=sys.stdout, stderr=sys.stderr, env=env)
    print r.wait()
