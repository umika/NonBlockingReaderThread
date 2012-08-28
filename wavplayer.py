#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wavplayer
Play a WAVE file.
'''

import sys, os, locale
import time
import wave
import pyaudio
import progressbar
from NonBlockingReaderThread import NonBlockingReaderThread

chunk = 1024

def main(fname):
  preenc = locale.getpreferredencoding()
  rt = NonBlockingReaderThread(sys.stdin)
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
  pause = False
  # while True:
  #   data = wf.readframes(chunk)
  #   if data is None or data == '': break
  for data in iter(lambda: wf.readframes(chunk), ''):
    try:
      count += len(data) / nb
      pgs.update(count)
      #while True:
      s = rt.get_nonblocking()
      if len(s) > 0:
        c = s[0]
        if c in '\x03\x1b\x20': rt.skip.set()
        if c in 'FfLl': continue
        if c in 'Pp': pause = True
        if c in 'Qq': pause = False
      if rt.skip.isSet(): break
      #if not pause: break
      #time.sleep(0.04) # 40ms
      stream.write(data)
    except KeyboardInterrupt, e:
      rt.skip.set()
  pgs.finish()
  stream.close()
  p.terminate()
  wf.close()
  rt.finalize()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'Plays a wave file.\n\nUsage: %s filename.wav' % sys.argv[0]
  else:
    main(sys.argv[1])
