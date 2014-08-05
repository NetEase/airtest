#!/bin/bash
#
set -eu
cd $(dirname $0)
export PYTHONPATH=$(cd ../; pwd) #:$PYTHONPATH
echo "DEBUG: PYTHONPATH=$PYTHONPATH"
python -c 'import airtest; print airtest.__version__'
py.test -v -l "$@"
