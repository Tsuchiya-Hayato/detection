
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from datetime import datetime as dt
import numpy as np
import chromedriver_binary
import cv2

driver = webdriver.Chrome("C:/Users/haya/Desktop/esp32/chromedriver/chromedriver.exe")
driver.get("http://192.168.100.119/") #TTGO CameraのサーバーのIP
url = "http://192.168.100.119/capture"
cascade_path = "C:/Users/haya/Desktop/haarcascades/haarcascade_frontalface_default.xml" #今回は正面の顔認識
element_size = driver.find_element_by_id('framesize')
indexNum = 4
element = driver.find_element_by_id('get-still') #撮影ボタンの指定
#連続撮影
while True:
    dt_now = dt.now()
    file_name = dt_now.strftime('C:/Users/haya/Pictures/%Y%m%d%H%M%S') + '.jpg'
    start = time.time()
    Select(element_size).select_by_index(indexNum)
    driver.execute_script("arguments[0].click();", element)
    response = requests.get(url)
    imagedata = response.content #バイナリデータで取得
    #バイナリデータをnp配列へ
    arr = np.asarray(bytearray(imagedata), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)  
    img = cv2.flip(img,1) #画像を鏡面に
    cv2.resize(img,(180,240))
    cascade = cv2.CascadeClassifier(cascade_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #推論
    face = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(30, 30))
    #BBoxの作成
    #顔認識した画像のみ保存
    if len(face) > 0:
        for (x, y, w, h) in face:
            cv2.rectangle(img, (x, y), (x + w, y+h), (0,0,300), 4)
        
        cv2.imwrite(file_name,img)    
    #認識結果の出力
    cv2.resize(img,(640,480))
    elapsed_time = round((time.time() - start),3)
    cv2.putText(img, str(elapsed_time)+' s', (10, 30),
               cv2.FONT_HERSHEY_PLAIN, 2,
               (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow("output", img)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()





