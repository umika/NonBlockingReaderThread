#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''playlist
Python 2.5 用に kill_process 実行しているが
subprocess.Popen で shell=True (cmd /C 相当) した process が
演奏が最後まで終わるまで終了しない
shell=False だとエラー
p.stdin.write(chr(3)) でも意味ない
PyAudio/sample01.py の方に問題あるのかも -> wavplayer.py に変更

Python 2.7 以上だと os.kill(p.pid, signal.CTRL_C_EVENT) も使える

ESC -> skip and stop    -> send chr(3) ^C
' ' -> skip             -> send chr(3) ^C
'p' -> pause
'q' -> play
'r' -> rew(rewind)
'f' -> ff(fast-forward)
'h' -> head
'j' -> next
'k' -> back
'l' -> tail
's' -> shuffle(random)
'''

import sys, os, locale
import random
import subprocess
import msvcrt

PLAYER = u'wavplayer.py'

def kill_process(pid):
  import ctypes
  PROCESS_TERMINATE = 1
  h = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
  ctypes.windll.kernel32.TerminateProcess(h, -1)
  ctypes.windll.kernel32.CloseHandle(h)

def main():
  preenc = locale.getpreferredencoding()
  lst = [fn for fn in os.listdir(u'./') if fn[-4:].upper() == u'.WAV']
  shuffle = False
  stop = False
  cur = 0
  while True:
    fname = lst[cur]
    cmd = [PLAYER, fname] # os.path.join(u'.', fname)
    p = subprocess.Popen([s.encode(preenc) for s in cmd],
      bufsize=4096, stdin=subprocess.PIPE,
      stdout=None, stderr=None, close_fds=False, shell=True)
    # p.communicate()
    skip = False
    while True:
      if skip or stop:
        sys.stdout.write('\7')
        p.stdin.write(chr(3))
        p.stdin.flush()
        try:
          p.kill() # or p.terminate() is not implemented for Python 2.5
        except:
          if os.name != 'nt': os.kill(p.pid, 9) # for Linux (signal.SIGKILL)
          else: kill_process(p.pid) # for Windows
        break
      if msvcrt.kbhit():
        c = msvcrt.getch()
        if c == chr(27): stop = True
        elif c == chr(32): skip = True
        elif c in 'Jj':
          if cur < len(lst) - 1: skip = True
        elif c in 'Kk':
          if cur > 0: skip, cur = True, cur - 2
        elif c in 'PpQqRrFfHhLl':
          p.stdin.write(c)
          p.stdin.flush()
        elif c in 'Ss': shuffle = not shuffle
      if p.poll() is not None: break
    if stop: break
    if shuffle:
      cur = random.randint(0, len(lst) - 1)
    else:
      cur += 1
      if cur >= len(lst): break

if __name__ == '__main__':
  main()
