#!/bin/bash -
python setup.py sdist upload -r ${1:-privatepypi}
