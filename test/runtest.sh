cd $(dirname $0)
export PYTHONPATH=$(cd ../; pwd) #:$PYTHONPATH
#export PYTHONPATH=$(cd ../;pwd)
echo $PYTHONPATH
#export PYTHONPATH=
python -c 'import airtest; print airtest.__version__'
py.test -v -l -s
