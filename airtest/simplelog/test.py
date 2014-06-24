import functools
import inspect
import sys

import simplelog
from decorators import *


BAR = "hello"

@dump_func()
def foo(name, name2):
    """
    This is a foo function
    """
    print ("hello " + name + name2)


if __name__ == "__main__":
    foo("max", "ben")
