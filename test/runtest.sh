cd $(dirname $0)
export PYTHONPATH=$PYTHONPATH:$(cd ../; pwd)
py.test -v -l
