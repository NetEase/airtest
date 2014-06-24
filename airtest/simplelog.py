#Copyright: This module has been placed under the public license

"""
This is the SimpleLog Documentation Package.

Package Structure:
==================

Modules:
-------
__init__.py
    Contains the SimpleLog class

Subpackages:
-----------
None yet
"""

__docformat__ = 'reStructuredText'

__version__ = '0.21'

__version_details__ = 'alpha release'
"""Extra version details (e.g. 'snapshot 2005-05-29, r3410', 'repository',
'release'), modified automatically & manually."""

__all__ = ["SimpeLog", "sl"]


import inspect
import logging
import logging.config
import logging.handlers
import os
#from decorators import dump_func, enable

SIMPLE_FORMAT = "[%(levelname)s]: %(asctime)s: %(message)s"
SIMPLE_FORMATTER = logging.Formatter(fmt = SIMPLE_FORMAT, datefmt = "%H:%m.%S")

class SimpleLog(logging.Logger):
    """
    Simplelog, because you have better things to do then worry about logging.

    @param:
    name - name of log, default is simple log (req)
    level - log level
    fname - filepath, defaults to <cwd>/simplelog.log
    path - default is current directory, 'tmp' puts log in /tmp folder
    verbose - if true, prints very detailed messages in dump
    quiet - print message to standard out?
    @return:
    simple log logger object
    """
    def __init__(self, name="simplelog", level=logging.NOTSET, 
                    path = None, verbose = False, quiet = False,
                    force = False):        
        super(SimpleLog, self).__init__(name, level)
        
        #Default is simplelog in current directory
        if (path == None):
            path = os.path.join(os.getcwd(), "simplelog.log")
        elif(path == "tmp"):
            path = "/tmp/simplelog.log"
        try:
            if (force): os.remove("path")
        except OSError:
            pass

        #State
        self.DIVIDER = "=========="
        self.path = path
        self.quiet = quiet
        self.sl_debug = logging.getLogger('alog')

        #Handlers
        if not quiet:
            self.sh = logging.StreamHandler()
            self.sh.setFormatter(SIMPLE_FORMATTER)

        fh = logging.FileHandler(filename=path)
        fh.setFormatter(SIMPLE_FORMATTER)

        self.setLevel(logging.DEBUG)
        self.addHandler(self.sh)
        self.addHandler(fh) #TODO: don't have this here
        
        #TODO: make this work
        self.sl_debug.setLevel(logging.DEBUG)
        self.sl_debug.addHandler(fh)

    def disable(self):
        """
        Dispale simplelog
        """
        self.handlers = [] #could this result in a memory leak?
        assert(self.handlers == [])
    
    def enable(self):
        """
        Enable simplelog
        """
        self.__init__(path = self.path, quiet = self.quiet)

    def quiet(self):
        """
        Remove the stream handler
        """
        self.quiet = True
        self.removeHandler(self.sh)
        
    def log(self, level, msg, *args, **kwargs):
        super(SimpleLog, self).log(level, msg, *args, **kwargs)
        self.sl_debug.log(level, msg, *args, **kwargs)

    def dump(self, var_name):
        """
        Prints the content of the string along with the string name
        @param:
        var_name - a string constant
        @return:
        none
        """
        #TODO: this doesn't work [critical, bug]
        try:
            value = locals()[var_name]
        except KeyError:
            value = globals()[var_name]
        self.log(self.level, self.var_name + ":" + str(value))

    @property
    def config():
        return self.config


#Singleton instance 
SL = sl = SimpleLog(path="/tmp/simplelog.log", force = True)

if __name__ == "__main__":
    print(sl)



