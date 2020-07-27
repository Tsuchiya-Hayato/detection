# ライブラリのインストール
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as tkk
import tkinter.font as font
import cv2
import sys
import os
import PIL.Image, PIL.ImageTk
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.utils.misc import Timer
from playsound import playsound

# アプリのクラスを作成
class CovidApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # ウィンドウの名前
        self.title(u"Phoenix Covid")
        # ウィンドウのサイズ
        self.geometry("800x680")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # VideoCaptureクラスを使用する
        self.cap = VideoCapture()
        self.detection = Detection()

        ### ラッパーフレームの作成 ###
        self.wrpFrm = tk.Frame(self)
        self.wrpFrm.configure(bg="white")
        # 縦横ともに3pxの余白で、rootウィンドウいっぱいに配置
        self.wrpFrm.grid(row=0, column=0, sticky="nsew")
        
        ### 評価結果フレームの作成 ###
        self.evalFrm = tk.Frame(self.wrpFrm)
        self.evalFrm.configure(bg="white")
        self.evalFrm.pack(padx=100, pady=2, fill="both", expand=1)
        # 検出人数を表示
        self.person_count = tkk.Label(self.evalFrm)
        self.person_count.configure(text="検出人数：",font=("",30),foreground="black", background="white")
        self.person_count.grid(padx=100,row=0, column=0, sticky="nsew")
        #密集度を算出
        self.eval_density = tkk.Label(self.evalFrm)
        self.eval_density.configure(text="密集度　：",font=("",30),foreground="black", background="white")
        self.eval_density.grid(padx=100,row=1, column=0, sticky="nsew")

        ### 動画表示フレームの作成 ###
        self.movieFrm = tk.Frame(self.wrpFrm)
        self.movieFrm.configure(bg="white")
        self.movieFrm.pack(padx=100, pady=2, fill="both", expand=1)
        # 動画表示キャンパスの配置
        self.movie_canvas = tk.Canvas(self.movieFrm, width = self.cap.width, height = self.cap.height)
        self.movie_canvas.pack()


        ### 閾値調整フレームの作成 ###
        self.threshhold = tk.Frame(self.wrpFrm)
        self.threshhold.configure(bg="white")
        # 縦横ともに3pxの余白で、rootウィンドウいっぱいに配置
        self.threshhold.pack(padx=100, pady=1, fill="both", expand=1)
        # スライダーの作成 #
        self.eval_density = tkk.Label(self.threshhold)
        self.eval_density.configure(text="密集閾値",font=("",25),foreground="black", background="white")
        self.eval_density.grid(row=0, column=0, sticky="nsew")
        self.var_distance = tk.DoubleVar(master=self.threshhold,value=0.5,)
        self.scale_distace = tk.Scale(master=self.threshhold, orient="h",variable=self.var_distance,from_=0.05, to=0.2,length=250, resolution=0.01)
        self.scale_distace.grid(row=1, column=0, sticky="nsew")

        # モデル推論の閾値スライダー #
        self.eval_model = tkk.Label(self.threshhold) 
        self.eval_model.configure(text="モデル判定閾値",font=("",25),foreground="black", background="white")
        self.eval_model.grid(row=0, column=2, sticky="nsew",padx=40)
        self.var_model = tk.DoubleVar(master=self.threshhold,value=0.5,)
        self.scale_model = tk.Scale(master=self.threshhold, orient="h",variable=self.var_model,from_=0.1, to=0.9,length=250, resolution=0.1)
        self.scale_model.grid(row=1, column=2, sticky="nsew",padx=40)


        #--------------------------------------------------------------------------
        ### 初期設定frame1 ###
        self.frame1 = tk.Frame(self)
        self.frame1.configure(bg="white")
        self.frame1.grid(row=0, column=0, sticky="nsew")

        ### カメラのIP入力
        self.camera_frame = tk.Frame(self.frame1)
        self.camera_frame.configure(bg="white")
        self.camera_frame.pack(padx=100, pady=10, expand=1)
        self.ip_camera = tkk.Label(self.camera_frame)
        self.ip_camera.configure(text="▽カメラのIPアドレスを入力▽",font=("",30),foreground="black", background="white")
        self.ip_camera.pack(pady=1, expand=1)
        self.ip_entry = tkk.Entry(self.camera_frame, font=("",20))
        self.ip_entry.insert(0, "192.168.100")
        self.ip_entry.pack(ipadx=25,ipady=10,pady=3, expand=1)

        ### music入力
        self.music_frame = tk.Frame(self.frame1)
        self.music_frame.configure(bg="white")
        self.music_frame.pack(padx=100, pady=1, fill="both", expand=1)
        # 音ファイル選択
        self.s = tk.StringVar()
        self.s.set('音声ファイルを指定')
        self.label1 = tkk.Label(self.music_frame)
        self.label1.configure(textvariable=self.s, font=("", '30'),foreground="black", background="white")
        self.label1.pack(pady=3, expand=1)
        # 参照ボタンの作成
        self.button1 = tk.Button(self.music_frame, text='ファイル選択', command=self.button1_clicked, font=("", 15))
        self.button1.pack(pady=1, expand=1)
        # 参照ファイルパス表示ラベルの作成
        self.music_file = tk.StringVar()
        self.file1_entry = tkk.Entry(self.music_frame, textvariable=self.music_file, width=40, font=("",15))
        self.file1_entry.pack(ipady=10, pady=3, expand=1)
        
        ### フレーム1からmainフレームに戻るボタン
        self.button_frame = tk.Frame(self.frame1)
        self.button_frame.configure(bg="white")
        self.button_frame.pack(padx=100, pady=1, fill="both", expand=1)
        self.back_button = tk.Button(self.button_frame,  text="検査開始", command=lambda:self.changePage(self.wrpFrm), font=("", '15'))
        self.back_button.pack(ipadx=25,ipady=10,pady=1, expand=1)

        ### main_frameを一番上に表示
        self.frame1.tkraise()

    def button1_clicked(self):
        fTyp = [("","*")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        self.filepath = filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
        self.music_file.set(self.filepath)

    def changePage(self, page):
        #入力値を得る
        self.ip_adress = self.ip_entry.get()
        self.music_adress = self.music_file.get()
        #画面遷移用の関数
        page.tkraise()
        # 更新作業
        self.update()

    def update(self):
        #画面更新
        distance_scale = self.scale_distace.get()
        thresh_scale = self.scale_model.get()
        try:
            ret, frame = self.cap.get_frame()
            frame,cnt = self.detection.eval_frame(frame,distance_scale,thresh_scale,self.music_adress)
            self.person_count.configure(text=("検出人数："+str(cnt)+'人'),font=("",30),foreground="black", background="white")
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
        self.alert_sum = 0
    def eval_frame(self,img,distance,threshold,music_path): #(画像、box間の距離閾値、モデル閾値)
        boxes, labels, probs = self.predictor.predict(img,10,threshold)
        cnt = 0
        for i in range(boxes.size(0)):
            
            box_1 = boxes[i, :]
            box_1x = int((box_1[0]+box_1[2])/2)
            box_1y = int((box_1[1]+box_1[3])/2)
            cv2.rectangle(img, (box_1[0], box_1[1]), (box_1[2], box_1[3]), (0, 255, 0), 3) #検出したものを一度全て緑に
            for j in range(boxes.size(0)):
                box_2 = boxes[j, :]
                box_2x = int((box_2[0]+box_2[2])/2)
                box_2y = int((box_2[1]+box_2[3])/2)
                box_distance  = (((box_1x - box_2x)**2)+(box_1y-box_2y)**2) ** 0.5
                box_distance = box_distance / (800**2 + 680**2) ** 0.5
                print(box_distance)
                if (i != j) & (box_distance < distance): #対象のモノを赤に
                    cnt = 1
                    cv2.line(img, (box_1x,box_1y),(box_2x,box_2y),(255,0,0),2)
                    cv2.rectangle(img, (box_1[0], box_1[1]), (box_1[2], box_1[3]), (255, 0, 0), 3)
                    cv2.rectangle(img, (box_2[0], box_2[1]), (box_2[2], box_2[3]), (255, 0, 0), 3)
        self.alert_sum += cnt
        if self.alert_sum == 3:
           #playsound(music_path)
            print('アラート')
            self.alert_sum = 0 
            

        return (img,boxes.size(0))

        

if __name__ == "__main__":
    app = CovidApp()
    app.mainloop()