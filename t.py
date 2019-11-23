#!/usr/bin/env python
import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose
from scipy import fft
from time import sleep, time
from os import system
from FSKChars import FSKToEnglish
import signal
import sys
import validate

#Sensitivity, 0.05: more Sensitive
#             0.1: Probably Ideal
#             1: less sensitive, 
SENSITIVITY= 0.05

#Bandwidth for detection 
BANDWIDTH = 60
#Set up audio sampler
SAMPLES = 1024
RATE = 88200
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=SAMPLES)
def sigHandler(s, fr):
   global p, stream
   stream.stop_stream()
   stream.close()
   p.terminate()     
   exit(0)
signal.signal(signal.SIGINT, sigHandler)
lo = 2300
hi = 2600
DETECT = [lo,hi]
o = ""
msg = ""
print "listening for code.."

def processBits(bits):
   curChr = ""
   sp = 0
   bt = 0
   buf = []
   dotMin = 1
   dashMin = 6
   space = 6
   m=""
   for bit in bits:
      if int(bit)==1:
         bt+=1
         sp=0
      else:
         sp+=1
         if bt >= dotMin and bt < dashMin:
            curChr+="."
            bt = 0
         elif bt>=dashMin:
            curChr+="-"
            bt = 0
         if sp >= space:
            if curChr in FSKToEnglish.keys():
               m+= FSKToEnglish[curChr] + " "
            else:
               m+= curChr
            curChr = ""
   t,c,y="",1,(m.replace(" ","")).split("0X")
   for x in y:
      if c == len(y):
         break
      t+=x
      c+=1
   return [m, validate.crc(t).upper()]
lockFlag = False
loScore = 0
while True:
   while stream.get_read_available()< SAMPLES: sleep(0.005)
   audioData  = fromstring(stream.read(
         stream.get_read_available()), dtype=short)[-SAMPLES:]
   normalizedData = audioData / 32768.0
   intensity = abs(fft(normalizedData))[:SAMPLES/2]
   frequencies = linspace(0.0, float(RATE)/2, num=SAMPLES/2)
   for tone in DETECT:
      try:
         if max(intensity[(frequencies < tone+BANDWIDTH) &
                          (frequencies > tone-BANDWIDTH )]) >\
            max(intensity[(frequencies < tone-100) &
                          (frequencies > tone-200)]) + SENSITIVITY:
            b = int(tone == hi)
            msg+=str(b)
            if not b:
               loScore += 1
               if not lockFlag:
                  print "Tone detected! Attempting to demodulate.."
                  lockFlag = True
            else:
               loScore = 0
            if loScore >= 25:
               loScore = 0
               while "101" in msg: #clean up stray bits
                  msg=msg.replace("101","111")
               while "010" in msg:
                  msg=msg.replace("010","000")
               msg=processBits(msg)
               xx,cc,m,rc = msg[0].replace(" ","").split("0X"),1,"",""
               for a in xx:
                  if cc==len(xx):
                     rc = a
                     break
                  m+=a
                  cc+=1
               rc="0X"+rc
               print "PKT: {}, C1: {}, C2:{} VERIFIED:{}"\
                  .format(m, msg[1], rc, (msg[1] == rc))
               msg=""
      except Exception as e:
          print e
          print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
          scoreIndex=0
          pass        
              

      
                  
