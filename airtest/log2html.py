#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
convert log to html report
'''

import os
import json
import time

import pystache

from airtest import base

def render(logfile, htmldir):
    '''
    parse logfile and render it to html
    '''
    assert os.path.exists(logfile)
    #htmldir = base.dirname(htmlfile)
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    items = []
    data = {
            'time': time.strftime('%Y/%m/%d %H:%M:%S'),
            'items': items, 
            }

    #items.append({'image': '.png'})

    for line in open(logfile):
        d = json.loads(line)
        timestamp = d.get('timestamp')
        _type = d.get('type')
        if _type == 'record':
            mem = d.get('mem')
            if mem:
                items.append({'time':timestamp, 'mem': mem})
            cpu = d.get('cpu')
            if cpu:
                items.append({'time':timestamp, 'cpu': cpu})
            #args = d.get('args')
            #args.extend([k+'='+v for k, v in d.get('kwargs').items()])
            #cmdstr = '{func}({argv})'.format(func=d.get('function'), 
            #        argv=' ,'.join(["'%s'"%s for s in args]))
            #items.append({'cmd': cmdstr})
        elif _type == 'snapshot':
            items.append({'time':timestamp, 'filename':d.get('filename')})
        #elif d.get('result'):
        #    data['result'] = {'status': d.get('result'), 'detail': d.get('detail')}

    tmpldir = os.path.join(base.dirname(__file__), 'htmltemplate')
    for name in os.listdir(tmpldir):
        if os.path.isdir(name):
            continue
        fullpath = os.path.join(tmpldir, name)
        content = open(fullpath).read().decode('utf-8')
        out = pystache.render(content, data)
        print fullpath
        #print out
        outpath = os.path.join(htmldir, name)
        with open(outpath, 'w') as file:
            file.write(out.encode('utf-8'))
        #tmplfile = os.path.join(base.dirname(__file__), 'template.html')

    #tmplfile = os.path.join(base.dirname(__file__), 'template.html')
    #template = open(tmplfile).read()

    #out = pystache.render(template.decode('utf-8'), data)
    #with open(htmlfile, 'w') as file:
    #    file.write(out.encode('utf-8'))

if __name__ == '__main__':
    render('testdata/airtest.log', 'tmp/out.html')
