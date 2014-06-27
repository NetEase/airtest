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

def render(logfile, htmlfile):
    '''
    parse logfile and render it to html
    '''
    assert os.path.exists(logfile)
    folder = base.dirname(htmlfile)
    if not os.path.exists(folder):
        os.makedirs(folder)
    tmplfile = os.path.join(base.dirname(__file__), 'template.html')
    template = open(tmplfile).read()
    data = {'items': [], 'time': time.strftime('%Y/%m/%d %H:%M:%S')}
    items = data['items']
    items.append({'image': 'xxx.png'})
    for line in open(logfile):
        d = json.loads(line)
        if d.get('function'):
            args = d.get('args')
            args.extend([k+'='+v for k, v in d.get('kwargs').items()])
            cmdstr = '{func}({argv})'.format(func=d.get('function'), 
                    argv=' ,'.join(["'%s'"%s for s in args]))
            items.append({'cmd': cmdstr})
        elif d.get('result'):
            data['result'] = {'status': d.get('result'), 'detail': d.get('detail')}


    out = pystache.render(template.decode('utf-8'), data)
    with open(htmlfile, 'w') as file:
        file.write(out.encode('utf-8'))

if __name__ == '__main__':
    render('testdata/airtest.log', 'tmp/out.html')
