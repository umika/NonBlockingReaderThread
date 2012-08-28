#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wavplayer
Play a WAVE file.
'''

import sys, os, locale
import wave
import pyaudio
import progressbar
import threading

chunk = 1024
skip = threading.Event()

def worker():
  skip.clear()
  fd = sys.stdin.fileno()
  while not skip.isSet():
    s = os.read(fd, 1) # DO NOT use sys.stdin.read(), it is buffered
    if s is None: continue
    if len(s) > 0 and s[0] == chr(3): break
  skip.set()

def main(fname):
  preenc = locale.getpreferredencoding()
  rt = threading.Thread(target=worker)
  rt.setDaemon(True) # to terminate this thread with the process
  rt.start()
  wf = wave.open(fname, 'rb')
  p = pyaudio.PyAudio()
  stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
  nframes = wf.getnframes()
  nb = wf.getnchannels() * wf.getsampwidth() # 2(LR) * 2bytes
  count = 0
  clip_fname = fname[:-4]
  if len(clip_fname) > 28:
    tmp = clip_fname.decode(preenc)
    clip_fname = (u'%s..%s' % (tmp[:6], tmp[-8:])).encode(preenc)
  widgets = ['%s(%s): ' % (clip_fname, nframes), progressbar.Percentage(),
    ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),
    ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
  pgs = progressbar.ProgressBar(widgets=widgets, maxval=nframes).start()
  # while True:
  #   data = wf.readframes(chunk)
  #   if data is None or data == '': break
  for data in iter(lambda: wf.readframes(chunk), ''):
    try:
      count += len(data) / nb
      pgs.update(count)
      stream.write(data)
    except KeyboardInterrupt, e:
      skip.set()
    if skip.isSet(): break
  pgs.finish()
  stream.close()
  p.terminate()
  wf.close()
  skip.set()
  rt._Thread__stop()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'Plays a wave file.\n\nUsage: %s filename.wav' % sys.argv[0]
  else:
    main(sys.argv[1])
