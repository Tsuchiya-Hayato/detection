from playsound import playsound
import subprocess
import sys
path = 'ans_wav_000.wav'
print('start')
popen = subprocess.Popen(['python','alert.py',path])
print(popen.poll())


