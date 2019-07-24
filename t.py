#!/usr/bin/env python

import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose
from scipy import fft
from time import sleep, time
from os import system
from FSKChars import FSKToEnglish
#Sensitivity, 0.05: more Sensitive
#             0.1: Probably Ideal
#             1: less sensitive, 
SENSITIVITY= 0.2

#Bandwidth for detection 
BANDWIDTH = 85
#Set up audio sampler
SAMPLES = 512
RATE = 88200
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=SAMPLES)
lo = 1600
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
   space = 8
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
   return m
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
            max(intensity[(frequencies < tone-1000) &
                          (frequencies > tone-2000)]) + SENSITIVITY:
            if not lockFlag:
               print "Carrier locked! Getting message.."
               lockFlag = True
            b = int(tone == hi)
            msg+=str(b)
            if not b:
               loScore += 1
            else:
               loScore = 0
            if loScore >= 14:
               loScore = 0
               while "101" in msg: #clean up stray bits
                  msg=msg.replace("101","111")
               while "010" in msg:
                  msg=msg.replace("010","000")
               system("clear")
               print processBits(msg)
      except Exception as e:
          print e
          scoreIndex=0
          pass
stream.stop_stream()
stream.close()
p.terminate()              
              

      
                  
