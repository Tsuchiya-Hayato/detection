import requests
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from datetime import datetime as dt
import numpy as np
import chromedriver_binary
import cv2
import PySimpleGUI as sg

#初期設定
driver = webdriver.Chrome("./chromedriver/chromedriver.exe")
driver.get("http://192.168.100.119/") #TTGO CameraのサーバーのIP
url = "http://192.168.100.119/capture"
cascade_path = "./haarcascades/haarcascade_frontalface_default.xml" #今回は正面の顔認識
element_size = driver.find_element_by_id('framesize')
indexNum = 4
element = driver.find_element_by_id('get-still') #撮影ボタンの指定

#アプリ設定
sg.theme('DarkAmber')
# define the window layout
layout = [
            [sg.Image(filename='', key='image')],
            [sg.Button('撮像', size=(14, 1), font='Helvetica 18')],

	        [sg.Text('判定結果',text_color='white',size=(15, 1), font='Helvetica 18'),
            sg.Radio('正解', 1, size=(8, 1), font='Helvetica 18', default=True, key='true'),
            sg.Radio('不正解', 1, size=(8, 1), font='Helvetica 18',key='false')],

            [sg.Button('保存して終了',button_color=('black','springgreen4'), size=(14, 1), font='Helvetica 18'),
            sg.Button('終了',button_color=('black','red'), size=(14, 1), font='Any 18')]  
        ]

# create the window and show it without the plot
window = sg.Window('ESP32 desktop app',layout,element_justification='center')

while True:
    event, values = window.read()

    if event == '撮像':
        #ファイル名決定
        dt_now = dt.now()
        file_name = dt_now.strftime('C:/Users/haya/Pictures/%Y%m%d%H%M%S') + '.jpg'

        
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
        if len(face) > 0:
            for (x, y, w, h) in face:
                cv2.rectangle(img, (x, y), (x + w, y+h), (0,0,300), 4)
                cv2.putText(img, 'human',(x+10, y+30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),1)

        imgbytes = cv2.imencode('.png', img)[1].tobytes()
        window['image'].update(data=imgbytes)

    if event == '保存して終了':
        if values['true']:
            try:
                dt_now = dt.now()
                file_name = dt_now.strftime('./good/%Y%m%d%H%M%S') + '.jpg'
                cv2.imwrite(file_name,img)   
                break
            except:
                print('撮像してください')
        
        if values['false']:
            try:
                dt_now = dt.now()
                file_name = dt_now.strftime('./bad/%Y%m%d%H%M%S') + '.jpg'
                cv2.imwrite(file_name,img)
                break
            except:
                print('撮像してください')

    if event == '終了':
        break



    
        


