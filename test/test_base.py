
import time

from airtest import base

def test_exec_cmd():
    p = base.exec_cmd('echo', 'hello')

def test_exec_cmd_shell():
    p = base.exec_cmd('echo hello', shell=True)

def test_check_output():
    output = base.check_output('echo hello')
    assert output == 'hello\n'

def test_go():
    d = {}
    @base.go
    def echo_hello(d):
        time.sleep(0.02)
        d['name'] = 'nice'
    p = echo_hello(d)
    assert d.get('name') == None
    p.join()
    assert d.get('name') == 'nice'

