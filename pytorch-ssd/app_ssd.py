

from vision.ssd.vgg_ssd import create_vgg_ssd, create_vgg_ssd_predictor
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.ssd.mobilenetv1_ssd_lite import create_mobilenetv1_ssd_lite, create_mobilenetv1_ssd_lite_predictor
from vision.ssd.squeezenet_ssd_lite import create_squeezenet_ssd_lite, create_squeezenet_ssd_lite_predictor
from vision.ssd.mobilenet_v2_ssd_lite import create_mobilenetv2_ssd_lite, create_mobilenetv2_ssd_lite_predictor
from vision.utils.misc import Timer
import PySimpleGUI as sg
import cv2
import numpy as np
import sys
import time

net_type = 'mb1-ssd'
model_path = './models/mb1-ssd-Epoch-1290-Loss-2.35230020682017.pth'
label_path = './models/voc-model-labels.txt'

class_names = [name.strip() for name in open(label_path).readlines()]
num_classes = len(class_names)

net = create_mobilenetv1_ssd(len(class_names), is_test=True)
net.load(model_path)
predictor = create_mobilenetv1_ssd_predictor(net, candidate_size=200)

cap = cv2.VideoCapture(0,cv2.CAP_V4L2)   # capture from camera
#cap = cv2.VideoCapture(0)
#cap.set(3, 1080)
#cap.set(4, 940)

sg.theme('DarkAmber')
# define the window layout
layout = [
              [sg.Image(filename='', key='image')],
              [sg.Checkbox('ヘルメット', size=(8, 1), font='Helvetica 14'),
               sg.Checkbox('溶接マスク', size=(8, 1), font='Helvetica 14'),
               sg.Checkbox('作業着', size=(8, 1), font='Helvetica 14'),
               sg.Checkbox('手袋', size=(8, 1), font='Helvetica 14')],

	      [sg.Text('エラー出力',text_color='white',size=(15, 1), font='Helvetica 16'),
               sg.Checkbox('ブザー', size=(8, 1), font='Helvetica 14'),
               sg.Checkbox('ライト', size=(8, 1), font='Helvetica 14')],

              [sg.Text('エラー判定基準',text_color='white',size=(15, 1), font='Helvetica 16'),
               sg.Slider(range=(1,10),key='ERROR-TIME',default_value=3,size=(20,15),orientation='horizontal',font='Helvetica 14')],

              [sg.Button('START',button_color=('black','springgreen4'), size=(14, 1), font='Helvetica 16'),
               sg.Button('STOP',button_color=('black','red'), size=(14, 1), font='Any 16'),
               sg.Button('EXIT',button_color=('black','white'), size=(14, 1), font='Helvetica 16'), ]]

# create the window and show it without the plot
window = sg.Window('Phoenix Safety',layout, location=(800, 400))
recording = False
count = 0
while True:
    start = time.time()
    event, values = window.read(timeout=20)
    error_time = values['ERROR-TIME']
    print('error_time:',error_time)
    print('count:',count)
    if event == 'EXIT' or event is None:
        break

    elif event == 'START':
        recording = True

    elif event == 'STOP':
        recording = False
        img = np.full((480, 640), 255)
        imgbytes = cv2.imencode('.png', img)[1].tobytes()
        window['image'].update(data=imgbytes)

    if recording:
        ret, orig_image = cap.read()
        if orig_image is None:
            continue

        orig_image = cv2.flip(orig_image, 1)
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        boxes, labels, probs = predictor.predict(image, 10, 0.4)
        print(boxes)
        print(labels)
        print(probs)
        for i in range(boxes.size(0)):
            box = boxes[i, :]

            if class_names[labels[i]] =='safe':
                label = 'safe' +  f": {probs[i]:.2f}"
                cv2.rectangle(orig_image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 4)
                cv2.rectangle(orig_image, (box[0], box[1]), (box[2], box[1]+(box[3]-box[1])//6), (0, 255, 0), -1)
                cv2.putText(orig_image, label,(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 0),2) 
                
            elif class_names[labels[i]] =='danger':
                label = 'Danger' +  f": {probs[i]:.2f}"
                cv2.rectangle(orig_image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 4)
                cv2.rectangle(orig_image, (box[0], box[1]), (box[2], box[1]+(box[3]-box[1])//6), (0, 0, 255), -1)
                cv2.putText(orig_image, label,(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 0),2)
                if count < error_time+1:
                    count += 1/10

           
            if count > error_time:
                cv2.putText(orig_image, str(round(count)),(10,60),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)

        interval = time.time() - start
        fps = round(1/interval,1)
        cv2.putText(orig_image, 'fps:'+str(fps),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)
	
        imgbytes = cv2.imencode('.png', orig_image)[1].tobytes()
        window['image'].update(data=imgbytes)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
