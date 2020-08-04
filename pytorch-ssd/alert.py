from playsound import playsound
import sys

path = sys.argv
flag = 1 #最初のサウンド
print("music start!!")
print(path[1])
if flag == 0:
    print('音声中')
elif flag == 1:
    flag = 0 #サウンド中は繰り返し鳴らさない
    playsound(path[1])
    flag = 1 #鳴り終わったらサウンド可能に
print("music end!!")