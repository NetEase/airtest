
import time

from airtest import base

def test_exec_cmd():
    p = base.exec_cmd('echo', 'hello')

def test_exec_cmd_shell():
    p = base.exec_cmd('echo hello', shell=True)

def test_check_output():
    output = base.check_output('echo hello')
    assert output == 'hello\n'

