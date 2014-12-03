#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# airtest web gui
#
import os
import flask
#from . import models

app = flask.Flask(__name__)

app.config['DEBUG'] = True


from .routers import home, api
app.register_blueprint(home.bp, url_prefix='')
app.register_blueprint(api.bp, url_prefix='/api')

# @app.route('/')
# def hello_world():
#     return 'Hello World!'

serve = app.run

if __name__ == '__main__':
    serve()