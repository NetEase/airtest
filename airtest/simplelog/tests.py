import simplelog
import unittest


class TestSimpleLog(unittest.TestCase):
    def setUp(self):
        self.sl = simplelog.sl

    def test_disable(self):
        """
        Remove all handlers from simplelog
        """
        self.sl.disable()
        self.assertTrue(self.sl.handlers == [])


@simplelog.dump_func()
def func1(arg1, arg2):
    """
    nul op func
    """
    return

class TestDecorators(unittest.TestCase):
    def setUp(self):
        self.sl = simplelog.sl

    def test_dump_func(self):
        return

