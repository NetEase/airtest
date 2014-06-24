#!/usr/bin/env python
# coding: utf-8
#

'''
Usage:
    air.test [--skip-install] [-c FILE] [-s SERIALNO]

Options:
    -h --help       Show this screen
    -c FILE         Specify config file [default: air.json]
    -s SERIALNO     Specify devices serialno(needed)
    --skip-install  Skip install apk [default: false]
'''

import json
import sys
import os
import urllib
import subprocess
from docopt import docopt

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

def urlretrieve(url, filename=None):
    print 'DOWNLOAD:', url, '->', filename
    return urllib.urlretrieve(url, filename)

def run_android(jsonfile, serialno, skip_install=False):
    d = json.load(open(jsonfile, 'r'))
    def xpath(*paths):
        v=d
        for p in paths:
            v = v.get(p, {})
        return v if v else None
    package = xpath('android', 'package')
    activity = xpath('android', 'activity')
    apk_url = xpath('android', 'apk_url')

    env = {'SERIALNO': serialno}
    if not skip_install:
        urlretrieve(apk_url, 'test.apk')
        exec_cmd('adb', '-s', serialno, 'install', '-r', 'test.apk')
        exec_cmd('adb', 'shell', 'am', 'start', '-n', '/'.join([package, activity]), timeout=10)
    exec_cmd('bash', '-c', xpath('cmd'), env=env)
    #try:
    #finally:
    #exec_cmd('adb', '-s', serialno, 'uninstall', package)
    #pass

def main():
    arguments = docopt(__doc__, version='0.1')
    print 'ARGUMENTS:', arguments
    cnf = arguments.get('-c')
    if not os.path.exists(cnf):
        print 'Can not found conf file: %s' %(cnf)
        sys.exit(1)
    serialno = arguments.get('-s')
    exec_cmd('adb', 'start-server', timeout=10)
    out = subprocess.check_output(['adb', '-s', serialno, 'get-state'])
    if out.strip() != 'device': 
        print 'device(%s) not ready, current state:%s' %(serialno, out.strip())
        sys.exit(2)
    run_android(cnf, serialno, skip_install=arguments.get('--skip-install'))

if __name__ == '__main__':
    main()
