#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
phone(android|iphone) autotest framework. gen can generate air.json
Usage:
    air.test gen <apk>
    air.test (runtest|install|uninstall) [-p PLATFORM] [SERIALNO]
    air.test log2html [--listen] [--port=PORT] <HTMLDIR>
    air.test snapshot [-p PLATFORM] [-r ROTATION] [SERIALNO]
    air.test all [--steps STEPS] [-H HTMLDIR] [-p PLATFORM] [SERIALNO]
    air.test update

Options:
    -h --help       Show this screen
    -p PLATFORM     android or iphone [default: android]
    -s SERIALNO     Specify devices serialno(needed)
    --steps STEPS   the steps one by one [default: install,runtest,log2html,uninstall]
    -H HTMLDIR      Save html report
    --port PORT     for log2html open a webserver to view report [default: 8888]
    -r ROTATION     rotation of device, one of UP,DOWN,LEFT,RIGHT
'''

__version__ = '0.1.0702'

import json
import sys
import os
import urllib
import subprocess
import re

from docopt import docopt
# from com.dtmilano.android.viewclient import ViewClient 

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
rotation = 'UP'

def xpath(*paths):
    v=F
    for p in paths:
        v = v.get(p, {})
    return v if v else None

def run_snapshot():
    global serialno
    if not serialno and platform=='android':
        print F
        ds = airtest.getDevices()
        print ds
        if len(ds) == 1:
            serialno=ds[0][0]
        else:
            sys.exit("too many devices, don't know which you want")
    assert serialno != None
    print 'snapshot', serialno
    app = airtest.connect(serialno, device=platform)
    app.globalSet(dict(tmpdir='.'))
    print 'ROTATION:', rotation
    app.globalSet(dict(rotation=rotation))
    app.takeSnapshot('screen.png')
    print 'screenshot save to "screen.png"'
    #if platform == 'android':
    #    c, _ = ViewClient.connectToDeviceOrExit(serialno=serialno)
    #    c.takeSnapshot().save('screen.png')
    #    print 'screenshot save to "screen.png"'
    #else:
    #    print 'not supported:', platform

def run_gen():
    airjson ={
      "cmd": "python main.py",
      "android": {
        "apk_url": "http://10.246.13.110:10001/demo-release-signed.apk",
        "package": "com.netease.xxx",
        "activity": "main.activity"
      }
    }
    with open('air.json', 'w') as file:
        json.dump(airjson, file, indent=4)
    print 'nice'

def run_install():
    if platform == 'android':
        apk_url = xpath(platform, 'apk_url')
        if re.match('^\w{1,2}tp://', apk_url):
            urlretrieve(apk_url, 'test.apk')
            apk_url = 'test.apk'
        exec_cmd('adb', '-s', serialno, 'install', '-r', apk_url)
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
            'AIRTEST_PHONENO': serialno, # not suggested, delete me in 2014/10/01
            'AIRTEST_DEVNO': serialno,
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
    print 'run this command manualy'
    print 'pip', 'install', '--upgrade', 'git+http://git.mt.nie.netease.com/hzsunshx/airtest.git'

def main():
    global F, platform, serialno, rotation
    arguments = docopt(__doc__, version='0.1')

    # set action
    action=''
    for act in ['all', 'install', 'log2html', 'runtest', 'snapshot', 'uninstall', 'update', 'gen']:
        if arguments.get(act):
            action = act
            break
    if not action:
        sys.exit('No action specified, see --help')
    print 'RUN action:', action

    # handle command in console
    cmd_name = sys.argv[1]
    from airtest import console
    func = console.COMMANDS.get(cmd_name)
    if func:
        return func.main(*sys.argv[2:])
    # else:sys.exit('cmd(%s) not exists' % cmd_name)

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
    rotation = arguments.get('-r', 'UP')
    if platform == 'android' and not arguments.get('SERIALNO'):
        devices = [dev for dev in airtest.getDevices() if dev[1] != 'unknown']
        if len(devices) != 1:
            sys.exit("can't determine which devices to use, please run: 'adb devices'")
        arguments['SERIALNO'] = devices[0][0]
        serialno = arguments['SERIALNO']

    if action in ['snapshot']:
        return globals().get('run_'+action)()

    print 'PREPARE platform: %s' %(platform)
    print 'PREPARE serialno: %s' %(serialno)
    #exec_cmd('adb', 'start-server', timeout=10)

    #print arguments
    if not os.path.exists(cnf) and action != 'gen':
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for p in SUBPROCESS:
            p.kill()
        print 'Exited by user'
