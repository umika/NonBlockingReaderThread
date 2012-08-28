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
import Queue

class NonBlockingReaderThread(threading.Thread):
  def __init__(self, pin, *args, **kwargs):
    self.pin = pin
    self.skip = threading.Event()
    self.skip.clear()
    self.que = Queue.Queue()
    super(NonBlockingReaderThread, self).__init__(target=self.worker,
      *args, **kwargs)
    self.setDaemon(True) # to terminate this thread with the process

  def run(self, *args, **kwargs):
    super(NonBlockingReaderThread, self).run(*args, **kwargs)

  def finalize(self):
    self.skip.set()
    self._Thread__stop()

  def worker(self):
    fd = self.pin.fileno()
    while True: # set 'True' with handling exception or 'not self.skip.isSet()'
      try:
        time.sleep(0.04) # 40ms
        s = os.read(fd, 1) # DO NOT use sys.stdin.read(), it is buffered
        if s is None: continue
        if len(s) > 0: self.que.put(s, False) # non blocking
      except:
        pass

  def get_nonblocking(self):
    try:
      return self.que.get(False) # non blocking
    except Queue.Empty, e:
      return ''

  def set_stdin_unbuffered(self):
    import ctypes
    m = ctypes.c_ulong(0)
    h = ctypes.windll.kernel32.GetStdHandle(-10) # stdin
    ctypes.windll.kernel32.GetConsoleMode(h, ctypes.byref(m)) # (m=487)
    ENABLE_LINE_INPUT = 0x0002
    n = ctypes.c_ulong(m.value & ~ENABLE_LINE_INPUT)
    ctypes.windll.kernel32.SetConsoleMode(h, n) # (n=485)

if __name__ == '__main__':
  rt = NonBlockingReaderThread(sys.stdin)
  rt.start()
  for i in xrange(20):
    print 'main: %d' % i
    time.sleep(0.5)
  rt.finalize() # _Thread__stop() is the best way to terminate os.read(fd, 1).
  # del rt # Delete thread but not terminate os.read(fd, 1) in worker thread.
  # os.close(0) # force close stdin to terminate os.read(fd, 1) but *DEAD LOCK*
  # rt.join(timeout=1.0) # must not call rt.join() because self.setDaemon(True)
