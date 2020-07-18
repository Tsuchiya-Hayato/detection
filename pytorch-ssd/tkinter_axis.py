# ライブラリのインストール
import tkinter as tk
import tkinter.ttk as tkk
import tkinter.font as font
import cv2
import sys
import PIL.Image, PIL.ImageTk
from vision.ssd.vgg_ssd import create_vgg_ssd, create_vgg_ssd_predictor
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.utils.misc import Timer

# アプリのクラスを作成
class CovidApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # ウィンドウの名前
        self.title(u"Phoenix Covid")
        # ウィンドウのサイズ
        self.geometry("800x640")
        # VideoCaptureクラスを使用する
        self.cap = VideoCapture()
        self.detection = Detection()
        ### ラッパーフレームの作成 ###
        self.wrpFrm = tk.Frame(self)
        self.wrpFrm.configure(bg="white")
        # 縦横ともに3pxの余白で、rootウィンドウいっぱいに配置
        self.wrpFrm.pack(padx=3, pady=3, fill="both", expand=1)
        #########################
        
        ### 評価結果フレームの作成 ###
        self.evalFrm = tk.Frame(self.wrpFrm)
        self.evalFrm.configure(bg="white")
        # 縦横ともに3pxの余白で、rootウィンドウいっぱいに配置
        self.evalFrm.pack(padx=100, pady=3, fill="both", expand=1)

        # 評価結果テキストを配置
        ## ウィジェット生成
        self.person_count = tkk.Label(self.evalFrm)
        self.person_count.configure(text="検出人数：",font=("",40),foreground="black", background="white")
        self.person_count.grid(row=0, column=0, sticky="w")

        ## ウィジェット生成
        self.eval_density = tkk.Label(self.evalFrm)
        self.eval_density.configure(text="密集度　：",font=("",40),foreground="black", background="white")
        self.eval_density.grid(row=1, column=0, sticky="w")

        ## スライダーの作成
        self.eval_density = tkk.Label(self.evalFrm)
        self.eval_density.configure(text="密集閾値",font=("",40),foreground="black", background="white")
        self.eval_density.grid(row=2, column=0, sticky="w")
        self.var = tk.IntVar(master=self.evalFrm,value=3,)
        self.scale = tk.Scale(master=self.evalFrm, orient="h",variable=self.var,from_=1, to=10,length=300)
        self.scale.grid(row=2, column=1, sticky="w")
        #########################

        ### 動画表示フレームの作成 ###
        self.movieFrm = tk.Frame(self.wrpFrm)
        self.movieFrm.configure(bg="white")
        # 縦横ともに3pxの余白で、rootウィンドウいっぱいに配置
        self.movieFrm.pack(padx=100, pady=3, fill="both", expand=1)

        # 動画表示キャンパスの配置
        self.movie_canvas = tk.Canvas(self.movieFrm, width = self.cap.width, height = self.cap.height)
        self.movie_canvas.pack()

        # 更新作業
        self.update()
        
        #########################
    def update(self):
        '''
        各キャンバスへの画像書き込み(opencvのimshow()的な処理)
        '''
        print(self.scale.get())
        # VideoCaptureクラスのget_frameで画像を取得
        try:
            ret, frame = self.cap.get_frame()
            frame,cnt = self.detection.eval_frame(frame,self.scale.get())
            self.person_count.configure(text=("検出人数："+str(cnt)+'人'),font=("",40),foreground="black", background="white")
        # 取得できなかったら
        except:
            print('update失敗')
            ret = False
            frame = 0
        if ret:
            print('ret=true')
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            #cam1_canvasに映像表示
            self.movie_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # 100ミリ秒ごとにupdate関数を実行
        self.after(300,self.update)
        
        
        
        
# 動画取得用のクラスを作成
class VideoCapture:
    def __init__(self):

        # カメラ読み込み
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print('カメラを読み込めませんでした。')
        print('camera読み込み')        
        #カメラの画面サイズ取得
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)    
    
    # 画像フレームの取得関数
    def get_frame(self):
        
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            # 画像読込成功：True・読込画像を返す
            # BGRからRGB画像に変更
            if ret:
                print('ret=true')
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # 画像読込失敗：False・Noneを返す
            else:
                print('ret=false')
                return (ret, None)
        else:
            #print('not open')
            return (ret, None)

class Detection():
    def __init__(self):
        model_path = './models/mb1-ssd-Epoch-1290-Loss-2.35230020682017.pth'
        label_path = './models/voc-model-labels.txt'
        self.class_names = [name.strip() for name in open(label_path).readlines()]
        net = create_mobilenetv1_ssd(len(self.class_names), is_test=True)
        net.load(model_path)
        
        self.predictor = create_mobilenetv1_ssd_predictor(net, candidate_size=200)
        print('Detection_init読み込み終了')


    def eval_frame(self,img,distance):
        print(distance)
        boxes, labels, probs = self.predictor.predict(img,10,0.3)
        pos_box = []  #bboxの中心の座標を格納するlist
        for i in range(boxes.size(0)):
            box = boxes[i, :]
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 4)
            pos_box.append([int((box[0]+box[2])/2), int((box[1]+box[3])/2)])
        #各bboxの中心同士の長さを計算
        #規定値より小さければ、線で結ぶ
        for box_1 in pos_box:
            for box_2 in pos_box:
                box_distance  = (((box_1[0]-box_2[0])**2)+(box_1[1]-box_2[1])**2) ** 0.5
                if box_distance < distance:
                    cv2.line(img, (box_1[0],box_1[1]),(box_2[0],box_2[1]),(0,255,0),1)
            # if self.class_names[labels[i]] =='safe':
            #     label = 'safe' +  f": {probs[i]:.2f}"
            #     cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 4)
            #     cv2.rectangle(img, (box[0], box[1]), (box[2], box[1]+(box[3]-box[1])//6), (0, 255, 0), -1)
            #     cv2.putText(img, label,(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 0),2) 
            # elif self.class_names[labels[i]] =='danger':
            #     label = 'Danger' +  f": {probs[i]:.2f}"
            #     cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 4)
            #     cv2.rectangle(img, (box[0], box[1]), (box[2], box[1]+(box[3]-box[1])//6), (0, 0, 255), -1)
            #     cv2.putText(img, label,(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 0),2)
        #cv2.putText(img, '検出人数:'+str(boxes.size(0)),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)
        print('eval_frame終了')

        return (img,boxes.size(0))

if __name__ == "__main__":
    app = CovidApp()
    app.mainloop()