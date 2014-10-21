#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
convert log to html report
'''

import fuckit

import os
import sys
import json
import time
import shutil

import pystache

from airtest import base

def render(logfile, htmldir):
    '''
    parse logfile and render it to html
    '''
    if not os.path.exists(logfile):
        sys.exit('logfile: %s not exists' %(logfile))
    #htmldir = base.dirname(htmlfile)
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    cpus, items = [], []
    fpss = []
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
            fps = d.get('fps')
            if fps:
                fpss.append([timestamp, fps])
        elif _type == 'snapshot':
            filename = d.get('filename')
            basename = os.path.basename(filename)
            with fuckit:
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
    data['fps_average'] = round(average(fpss), 2)

    tmpldir = os.path.join(base.dirname(__file__), 'htmltemplate')
    for name in os.listdir(tmpldir):
        fullpath = os.path.join(tmpldir, name)
        outpath = os.path.join(htmldir, name)
        if os.path.isdir(fullpath):
            shutil.rmtree(outpath, ignore_errors=True)
            shutil.copytree(fullpath, outpath)
            continue
        if fullpath.endswith('.swp'):
            continue
        content = open(fullpath).read().decode('utf-8')
        out = pystache.render(content, data)
        print fullpath
        with open(outpath, 'w') as file:
            file.write(out.encode('utf-8'))

        # store json data file, for other system
        with open(os.path.join(htmldir, 'data.json'), 'w') as file:
            json.dump(data, file)

if __name__ == '__main__':
    render('testdata/airtest.log', 'tmp/out.html')
