cd $(dirname $0)
export PYTHONPATH=$(cd ../; pwd):$PYTHONPATH
py.test -v -l
