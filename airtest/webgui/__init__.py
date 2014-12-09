#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# airtest web gui
#
import os
import flask
#from . import models
from .routers import utils

app = flask.Flask(__name__)

app.config['DEBUG'] = True


from .routers import home, api
app.register_blueprint(home.bp, url_prefix='')
app.register_blueprint(api.bp, url_prefix='/api')

def serve(*args, **kwargs):
    print 'Clean tempfiles ...'
    for file in os.listdir(utils.TMPDIR):
        filepath = os.path.join(utils.TMPDIR, file)
        if os.path.isfile(filepath):
            os.unlink(filepath)
    app.run(*args, **kwargs)

if __name__ == '__main__':
    serve()