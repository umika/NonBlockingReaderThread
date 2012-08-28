#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''NonBlockingReaderThread
SetConsoleMode
http://msdn.microsoft.com/en-us/library/ms686033%28v=vs.85%29
ENABLE_LINE_INPUT = 0x0002
'''

import sys, os
import time
import threading

class NonBlockingReaderThread(threading.Thread):
  def __init__(self, *args, **kwargs):
    super(NonBlockingReaderThread, self).__init__(target=self.worker,
      *args, **kwargs)
    self.setDaemon(True) # to terminate this thread with the process

  def run(self, *args, **kwargs):
    super(NonBlockingReaderThread, self).run(*args, **kwargs)

  def worker(self):
    print 'start'
    c = 0
    while True:
      time.sleep(1.5)
      print 'worker: %d' % c
      c += 1
    print 'end'

  def set_stdin_unbuffered(self):
    import ctypes
    m = ctypes.c_ulong(0)
    h = ctypes.windll.kernel32.GetStdHandle(-10) # stdin
    ctypes.windll.kernel32.GetConsoleMode(h, ctypes.byref(m)) # (m=487)
    ENABLE_LINE_INPUT = 0x0002
    n = ctypes.c_ulong(m.value & ~ENABLE_LINE_INPUT)
    ctypes.windll.kernel32.SetConsoleMode(h, n) # (n=485)

if __name__ == '__main__':
  rt = NonBlockingReaderThread()
  rt.start()
  for i in xrange(20):
    print 'main: %d' % i
    time.sleep(0.5)
  rt._Thread__stop() # This is the best way to terminate os.read(fd, 1).
  # del rt # Delete thread but not terminate os.read(fd, 1) in worker thread.
  # os.close(0) # force close stdin to terminate os.read(fd, 1) but *DEAD LOCK*
  # rt.join(timeout=1.0) # must not call rt.join() because self.setDaemon(True)
