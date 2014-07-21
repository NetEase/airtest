#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# coding: utf-8
#

'''
phone(android|iphone) autotest framework
Usage:
    air.test (runtest|install|uninstall) [-p PLATFORM] [SERIALNO]
    air.test log2html [--listen] [--port=PORT] <HTMLDIR>
    air.test snapshot [-p PLATFORM] [SERIALNO]
    air.test all [--steps STEPS] [-H HTMLDIR] [-p PLATFORM] [SERIALNO]
    air.test update

Options:
    -h --help       Show this screen
    -p PLATFORM     android or iphone [default: android]
    -s SERIALNO     Specify devices serialno(needed)
    --steps STEPS   the steps one by one [default: install,runtest,log2html,uninstall]
    -H HTMLDIR      Save html report
    --port PORT     for log2html open a webserver to view report [default: 8888]
'''

__version__ = '0.1.0702'

import json
import sys
import os
import urllib
import subprocess

from docopt import docopt
from com.dtmilano.android.viewclient import ViewClient 

import airtest
from airtest.base import exec_cmd
from airtest import log2html, jsonlog

def urlretrieve(url, filename=None):
    print 'DOWNLOAD:', url, '->', filename
    return urllib.urlretrieve(url, filename)

F = {} #json.load(open(jsonfile, 'r'))
SUBPROCESS = []
platform = 'android'
serialno = None

def xpath(*paths):
    v=F
    for p in paths:
        v = v.get(p, {})
    return v if v else None

def run_snapshot():
    global serialno
    if not serialno:
        ds = airtest.getDevices()
        print ds
        if len(ds) == 1:
            serialno=ds[0][0]
        else:
            sys.exit("too many devices, don't know which you want")

    print 'snapshot', serialno
    if platform == 'android':
        c, _ = ViewClient.connectToDeviceOrExit(serialno=serialno)
        c.takeSnapshot().save('screen.png')
        print 'screenshot save to "screen.png"'
    else:
        print 'not supported:', platform

def run_install():
    if platform == 'android':
        urlretrieve(xpath(platform, 'apk_url'), 'test.apk')
        exec_cmd('adb', '-s', serialno, 'install', '-r', 'test.apk')
        package, activity = xpath(platform, 'package'), xpath(platform, 'activity')
        exec_cmd('adb', '-s', serialno, 'shell', 'am', 'start', '-n', '/'.join([package, activity]), timeout=10)
    else:
        print 'not supported:', platform

def run_uninstall():
    if platform == 'android':
        exec_cmd('adb', '-s', serialno, 'uninstall', xpath(platform, 'package'))
    else:
        print 'not supported:', platform

def run_runtest():
    env = {
            'SERIALNO': serialno, 
            'AIRTEST_PHONENO': serialno,
            'AIRTEST_APPNAME': xpath(platform, 'package')}
    exit_code = exec_cmd(xpath('cmd'), timeout=30*60, shell=True, env=env)
    assert exit_code == 0

def run_log2html():
    if F.get('logfile') and F.get('htmldir'):
        log2html.render(F.get('logfile'), F.get('htmldir'))
        if F.get('listen'):
            p = subprocess.Popen(['python', '-mSimpleHTTPServer', F.get('port')], stdout=sys.stdout, stderr=sys.stderr, cwd=F.get('htmldir'))
            SUBPROCESS.append(p)
            p.wait()
            #os.system('cd %s; python -mSimpleHTTPServer %s' %(F.get('htmldir'), F.get('port')))

def run_update():
    exec_cmd('pip', 'install', '--upgrade', 'git+http://git.mt.nie.netease.com/hzsunshx/airtest.git')

def main():
    global F, platform, serialno
    arguments = docopt(__doc__, version='0.1')

    # set action
    action=''
    for act in ['all', 'install', 'log2html', 'runtest', 'snapshot', 'uninstall', 'update']:
        if arguments.get(act):
            action = act
            break
    if not action:
        sys.exit('No action specified, see --help')
    print 'RUN action:', action

    # load conf
    cnf = 'air.json'
    if os.path.exists(cnf):
        F = json.load(open(cnf))
    if not 'logfile' in F:
        logfile = 'log/airtest.log'
        F['logfile'] = logfile
        os.environ['AIRTEST_LOGFILE'] = logfile

    F['htmldir'] = arguments.get('<HTMLDIR>') or arguments.get('-H')
    F['port'] = arguments.get('--port')
    F['listen'] = arguments.get('--listen')

    if action in ['log2html', 'update']:
        return globals().get('run_'+action)()

    # check phoneno and platform
    serialno = arguments['SERIALNO']
    platform = arguments.get('-p', 'android')
    if platform == 'android' and not arguments.get('SERIALNO'):
        devices = [dev for dev in airtest.getDevices() if dev[1] != 'unknown']
        if len(devices) != 1:
            sys.exit("can't determine which devices to use, please run: 'adb devices'")
        arguments['SERIALNO'] = devices[0][0]

    if action in ['snapshot']:
        return globals().get('run_'+action)()

    print 'PREPARE platform: %s' %(platform)
    print 'PREPARE serialno: %s' %(serialno)
    exec_cmd('adb', 'start-server', timeout=10)

    #print arguments
    if not os.path.exists(cnf):
        sys.exit('config file require: %s' %(cnf))
    if action == 'all':
        exitcode = 0
        for step in arguments['--steps'].split(','):
            fn = globals().get('run_'+step)
            if not fn or not callable(fn):
                sys.exit('no such step: %s' %(step))
            print 'STEP:', step
            try:
                fn()
            except Exception as e:
                jsonlog.JSONLog(logfile).writeline({'type':'cli', 'step':step, 'result':'failed', 'detail': str(e)})
                exitcode=1

        sys.exit(exitcode)
        return
    if action in ['install', 'uninstall', 'log2html', 'runtest']:
        print 'RUN:', action
        return globals().get('run_'+action)()
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for p in SUBPROCESS:
            p.kill()
        print 'Exited by user'
