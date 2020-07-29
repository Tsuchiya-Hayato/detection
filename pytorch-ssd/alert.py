from playsound import playsound
import sys

path = sys.argv
print("music start!!")
print(path[1])
playsound(path[1])
print("music end!!")