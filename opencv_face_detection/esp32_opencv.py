import requests
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from datetime import datetime as dt
import numpy as np
import chromedriver_binary
import cv2

dt_now = dt.now()
print('a')
driver = webdriver.Chrome("C:/Users/haya/Downloads/chromedriver/chromedriver.exe")
driver.get("http://192.168.100.119/")
print('B')
element = driver.find_element_by_id('framesize')
indexNum = 2
Select(element).select_by_index(indexNum)
element = driver.find_element_by_id('get-still')
driver.execute_script("arguments[0].click();", element)
time.sleep(0.5) #sleep(秒指定)
url = "http://192.168.100.119/capture"
file_name = dt_now.strftime('C:/Users/haya/Pictures/%Y%m%d%H%M') + '.jpg'
response = requests.get(url)
imagedata = response.content
'''
print('c')
with open(file_name, "wb") as aaa:
    aaa.write(imagedata)
'''
time.sleep(0.5) #sleep(秒指定)
driver.close()

#opencvで顔認識
#参考　https://qiita.com/FukuharaYohei/items/ec6dce7cc5ea21a51a82
cascade_path = "C:/Users/haya/Desktop/haarcascades/haarcascade_frontalface_default.xml"

arr = np.asarray(bytearray(imagedata), dtype=np.uint8)
img = cv2.imdecode(arr, -1)  # 'load it as it is'

#img = cv2.imread(file_name)
cascade = cv2.CascadeClassifier(cascade_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

face = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(30, 30))
color = (255, 255, 255)
print('D')
if len(face) > 0:

    for (x, y, w, h) in face:
        cv2.rectangle(img, (x, y), (x + w, y+h), (0,0,300), 4)
#認識結果の出力
print(img.shape)
cv2.imshow("output", img)
cv2.waitKey(0)
cv2.destroyAllWindows()