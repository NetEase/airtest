#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
import urllib
import json

import airtest
import click
from airtest import log2html as airlog2html
from airtest import androaxml

__debug = False

def _wget(url, filename=None):
    print 'DOWNLOAD:', url, '->', filename
    return urllib.urlretrieve(url, filename)

def _run(*args, **kwargs):
    if __debug:
        click.echo('Exec: %s [%s]' %(args, kwargs))
    kwargs['stdout'] = kwargs.get('stdout') or sys.stdout
    kwargs['stderr'] = kwargs.get('stderr') or sys.stderr
    p = subprocess.Popen(args, **kwargs)
    p.wait()

def _get_apk(config_file, cache=False):
    if os.path.exists(config_file):# compatiable with cli-1
        with open(config_file) as file:
            cfg = json.load(file)
            apk = cfg.get('apk')
            if apk:
                return apk
            apk = cfg.get('android', {}).get('apk_url') 
            if apk: 
                return apk
    apk = raw_input('Enter apk path or url: ')
    assert apk.lower().endswith('.apk')
    # FIXME: save to file
    with open(config_file, 'wb') as file:
        file.write(json.dumps({'apk': apk}))
    if re.match('^\w{1,2}tp://', apk):
        if cache and os.path.exists('tmp.apk'):
            return 'tmp.apk'
        _wget(apk, 'tmp.apk')
        apk = 'tmp.apk'
    return apk

@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Show verbose information')
def cli(verbose):
    global __debug
    __debug = verbose

@cli.command()
@click.argument('apkfile', type=click.Path(exists=True))
def inspect(apkfile):
    pkg, act = androaxml.parse_apk(apkfile)
    click.echo('Package Name: "%s"' % pkg)
    click.echo('Activity: "%s"' % act)

@cli.command()
@click.option('--logfile', default='log/airtest.log', help='airtest log file path',
        type=click.Path(exists=True, dir_okay=False), show_default=True)
@click.option('--listen', is_flag=True, help='open a web serverf for listen')
@click.option('--port', default=8800, help='listen port', show_default=True)
@click.argument('outdir', type=click.Path(exists=False, file_okay=False))
def log2html(logfile, outdir, listen, port):
    airlog2html.render(logfile, outdir)
    if listen:
        click.echo('Listening on port %d ...' % port)
        _run('python', '-mSimpleHTTPServer', str(port), cwd=outdir)

@cli.command()
@click.option('--phoneno', help='If multi android dev connected, should specify serialno')
@click.option('--platform', default='android', type=click.Choice(['android', 'windows', 'ios']), show_default=True)
@click.option('--out', default='snapshot.png', type=click.Path(dir_okay=False),
        help='out filename [default: "snapshot.png"]', show_default=True)
def snapshot(phoneno, platform, out):
    try:
        app = airtest.connect(phoneno=phoneno, device=platform)
        app.takeSnapshot(out)
    except Exception, e:
        click.echo(e)

@cli.command()
@click.option('--no-start', is_flag=False, help='Start app after successfully installed')
@click.option('--conf', default='air.json', type=click.Path(dir_okay=False), help='config file', show_default=True)
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.argument('apk', required=False)
def install(no_start, conf, serialno, apk):
    apk = _get_apk(conf)

    adbargs = ['adb']
    if serialno:
        adbargs.extend(['-s', serialno])
    args = adbargs + ['install', '-r', apk]
    # install app
    _run(*args)

    if no_start:
        return
    pkg, act = androaxml.parse_apk(apk)
    args = adbargs + ['shell', 'am', 'start', '-n', pkg+'/'+act]
    _run(*args)

@cli.command()
@click.option('--conf', default='air.json', type=click.Path(dir_okay=False), help='config file')
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.argument('apk', required=False)
def uninstall(conf, serialno, apk):
    if not apk:
        apk = _get_apk(conf, cache=True)
    pkg, act = androaxml.parse_apk(apk)
    args = ['adb']
    if serialno:
        args.extend(['-s', serialno])
    args += ['uninstall', pkg]
    _run(*args)

if __name__ == '__main__':
    cli()

################################################################

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print 'Exited by user'
