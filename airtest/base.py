#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import random
import string
import time
import logging
import threading

random.seed(time.time())
logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level = logging.DEBUG) 

def getLogger(name='root'):
    return logging.getLogger(name)

log = getLogger('base')

def makedirs(dirname):
    try:
        os.makedirs(dirname)
    except:
        pass

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
    for key in env: env[key] = str(env[key]).encode('utf-8') # fix encoding

    timeout = kwargs.get('timeout', 120)
    shell = kwargs.get('shell', False)
    try:
        import sh
        print 'RUN(timeout=%ds):'%(timeout), ' '.join(cmds)
        if shell:
            cmds = list(cmds)
            cmds[:0] = ['bash', '-c']
        c = sh.Command(cmds[0])
        r = c(*cmds[1:], _err_to_out=True, _out=sys.stdout, _env=env, _timeout=timeout)
    except ImportError:
        print 'RUN(timeout=XX):', ' '.join(cmds)
        if shell:
            cmds = ' '.join(cmds)
        r = subprocess.Popen(cmds, env=env, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
    print r.wait()

def check_output(cmd):
    return subprocess.check_output(cmd, shell=True)
    
def random_name(name):
    out = []
    for c in name:
        if c == 'X':
            c = random.choice(string.ascii_lowercase)
        out.append(c)
    return ''.join(out)


def wait_until(fn, interval=0.5, max_retry=10, args=(), kwargs={}):
    '''
    @return True(when found), False(when not found)
    '''
    # log.debug('wait func: %s', fn.__name__)
    retry = 0
    while retry < max_retry:
        retry += 1
        ret = fn(*args, **kwargs)
        if ret:
            return ret
        log.debug('wait until: %s, sleep: %s', fn.__name__, interval)
        time.sleep(interval)
    return None

def go(fn):
    log.info('run func(%s) in background', fn.__name__)
    def decorator(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
        return t
    return decorator
