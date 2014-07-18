cd $(dirname $0)
export PYTHONPATH=$(cd ../; pwd)
py.test -v -l
