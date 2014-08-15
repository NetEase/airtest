# coding: utf-8

import uuid
import threading
import time
import Queue

def go(func, *args, **kwargs):
    t = threading.Thread(target=func, args=args, kwargs=kwargs)
    t.setDaemon(True)
    t.start()
    return t

class Monitor(object):
    def __init__(self):
        self._tasks = {}
        self._running = False
        self._cycle = 1.0
        go(self._drain)

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def running(self):
        return self._running

    def addfunc(self, func, *args, **kwargs):
        key = str(uuid.uuid4())
        self._tasks[key] = [func, args, kwargs]
        return key

    def delfunc(self, key):
        del(self._tasks[key])

    def _drain(self):
        while True:
            if not self._running:
                time.sleep(0.5)
                continue
            for task in self._tasks.values():
                func, args, kwargs = task
                go(func, *args, **kwargs)
            time.sleep(max(0.5, self._cycle))

if __name__ == '__main__':
    m = Monitor()
    def say(msg = 'hello'):
        print 'say:', msg
    m.addfunc(say, 'hi')
    key = m.addfunc(say, 'hey')
    m.start()
    time.sleep(2)
    m.delfunc(key)
    time.sleep(2)
    print 'stop', m.running()
    m.stop()
    time.sleep(2)

