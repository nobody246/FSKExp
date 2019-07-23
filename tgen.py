import pyaudio
import numpy as np
from time import sleep
from FSKChars import englishToFSK, nato

#todo add as params
volume = 1
fs = 44100 
duration = .08
lo = 1600.0
hi = 2600.0
freqs = [lo,hi]
useNato = True
messageStr ="""        dflksjfnsdf * JHBKJHB * QWODL * fbqxdaz * qpwoiaccvbf *       """
message=""
for s in messageStr.upper():
      if not useNato or (useNato and s == "*"):
            if s == "*":
                  c = 0
                  while c<3:
                        message+=englishToFSK["X"] +\
                                  englishToFSK["interChar"]
                        c+=1
            else:
                  message+=englishToFSK[s] + englishToFSK["interChar"]
      else:
            for S in nato[s]:
                  message+=englishToFSK[S] + englishToFSK["interChar"]
            message += englishToFSK[" "]
p = pyaudio.PyAudio()
def playFreq(f):
   global fs, volume, sp, duration
   samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).\
             astype(np.float32)
   stream.write(volume * samples)
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)
while True:
    for m in message:
       playFreq(freqs[int(m)])
stream.stop_stream()
stream.close()
p.terminate()
