#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def dirname(name):
    if os.path.isabs(name):
        return os.path.dirname(name)
    return os.path.dirname(os.path.abspath(name))
