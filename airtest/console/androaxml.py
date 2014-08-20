#!/usr/bin/env python

# This file is part of Androguard.
#
# Copyright (C) 2012, Anthony Desnos <desnos at t0t0.fr>
# All rights reserved.
#
# Androguard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Androguard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Androguard.  If not, see <http://www.gnu.org/licenses/>.

import os
__dir__ = os.path.relpath(os.path.dirname(os.path.abspath(__file__))) 

import sys
sys.path.append(os.path.join(__dir__, "androguard.zip"))

from androguard.core.bytecodes import apk


def xml2parse(dom): #, strformat='$package/$activity'):
    root = dom.getElementsByTagName("manifest")[0]
    package = root.getAttribute('package')
    activity = ''
    for e in root.getElementsByTagName('activity'):
        name = e.getAttribute('android:name')
        t = e.getElementsByTagName('intent-filter')
        if t:
            activity = name
    return (package, activity)

def parse_apk(filename):
    ''' return (package, activity) '''
    a = apk.APK(filename)
    dom = a.get_android_manifest_xml()
    return xml2parse(dom)

