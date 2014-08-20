#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from . import androaxml

def main(*args):
    ''' gen <apk> '''
    if len(args) != 1:
        sys.exit("Usage: air.test gen <apk>")

    apk_file = args[0]
    (package, activity) = androaxml.parse_apk(apk_file)
    print 'PACKAGE: %s\nACTIVITY: %s' %(package, activity)
    airjson ={
      "cmd": "python main.py",
      "android": {
        "apk_url": apk_file,
        "package": package,
        "activity": activity
      }
    }
    with open('air.json', 'w') as file:
        json.dump(airjson, file, indent=4)
    print 'Finish generate air.json'