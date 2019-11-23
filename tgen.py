import pyaudio
import numpy as np
from time import sleep
from FSKChars import englishToFSK, nato
import signal
import validate
#todo add as params
volume = 1
fs = 44100 
duration = .12
lo = 2300.0
hi = 2600.0
freqs = [lo,hi]
useNato = False #set to True to broadcast chars phoenetically
messageStr =""" 0123456789 2019 2020 1987 1808 KING CARLITUS WAS THE KING OF THE LAND THEQUICKBROWNFOXJUMPEDOVERTHELAZYDOG THIS IS A TEST OF THE PUBLIC ANNOUNCEMENT SYSTEM THIS IS NOT AN EMERGENCY IT IS ONLY A TEST 18004444444 TANGOHOTELECFOQUEBECUNIFORMINDIACHARLIEKILOBRAVOROMEOOSCARWHISKEYNOVEMIERFOXTROTOSCARXRAYJULIETTUNIFORMMIKEPAPAECHODELTAOSCARVICTORECHOROMEOTANGOHOTELECHOLIMAALPHAZULUYANKEEDELTAOSCARGOLF ABCDEFGHIJKLMNOPQRSTUVWXYZ      """
message=""
m=""
for s in messageStr.upper():
      if not useNato or (useNato and s == "*"):
            if s == "*":
                  c = 0
                  while c<3:
                        m+="X"
                        message+=englishToFSK["X"] +\
                            englishToFSK["interChar"]
                        c+=1
            elif s == " ":
                  for x in validate.crc(m).upper():
                        message+=englishToFSK[x] + englishToFSK["interChar"]
                  message+=englishToFSK[s] + englishToFSK["interChar"]
                  m=""
                  continue
            else:
                  m+=s
                  message+=englishToFSK[s] + englishToFSK["interChar"]
      else:
            for S in nato[s]:
                  message+=englishToFSK[S] + englishToFSK["interChar"]
            message+= englishToFSK[" "]
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
def sigHandler(s, fr):
   global p, stream
   stream.stop_stream()
   stream.close()
   p.terminate()     
   exit(0)
signal.signal(signal.SIGINT, sigHandler)
while True:
    for m in message:
       playFreq(freqs[int(m)])
stream.stop_stream()
stream.close()
p.terminate()
