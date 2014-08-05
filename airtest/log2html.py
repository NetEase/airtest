#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
convert log to html report
'''

import os
import json
import time
import shutil

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
    cpus, items = [], []
    mems, imgs = [], []
    data = {
            'info': {
                'generated_time': time.strftime('%Y/%m/%d %H:%M:%S'),
            },
            'items': items, 
            #'cpus': cpus,
            'cpu_data': None,
            'mem_data': None,
            #'mems': mems,
            'images': imgs,
            }
    info = data.get('info')

    start_time = 0
    for line in open(logfile):
        d = json.loads(line)
        time_format = '%Y/%m/%d %H:%M:%S'
        timestamp = d.get('timestamp') - start_time
        _type = d.get('type')
        if _type == 'start':
            start_time = d.get('timestamp')
        elif _type == 'record':
            mem = d.get('mem')
            if mem:
                mems.append([timestamp, mem])
            cpu = d.get('cpu')
            if cpu:
                cpus.append([timestamp, cpu])
        elif _type == 'snapshot':
            filename = d.get('filename')
            basename = os.path.basename(filename)
            shutil.copyfile(filename, os.path.join(htmldir, basename))
            imgs.append({'time':timestamp, 'filename':basename})
        #elif d.get('result'):
        #    data['result'] = {'status': d.get('result'), 'detail': d.get('detail')}
    data['cpu_data'] = json.dumps(cpus)
    data['mem_data'] = json.dumps(mems)
    def average(ss):
        if ss:
            return reduce(lambda x,y: x+y, [value for _,value in ss])/float(len(ss))
        return 0.0

    data['cpu_average'] = round(average(cpus), 2)
    data['mem_average'] = round(average(mems), 2)

    tmpldir = os.path.join(base.dirname(__file__), 'htmltemplate')
    for name in os.listdir(tmpldir):
        if os.path.isdir(name) or name.endswith('.swp'):
            continue
        fullpath = os.path.join(tmpldir, name)
        content = open(fullpath).read().decode('utf-8')
        out = pystache.render(content, data)
        print fullpath
        outpath = os.path.join(htmldir, name)
        with open(outpath, 'w') as file:
            file.write(out.encode('utf-8'))

        # store json data file, for other system
        with open(os.path.join(htmldir, 'data.json'), 'w') as file:
            json.dump(data, file)

if __name__ == '__main__':
    render('testdata/airtest.log', 'tmp/out.html')
