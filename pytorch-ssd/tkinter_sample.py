# ライブラリのインストール
import tkinter as tk
import tkinter.ttk as tkk
import tkinter.font as font
import cv2
import PIL.Image, PIL.ImageTk

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
        self.person_count.pack(anchor="w")

        ## ウィジェット生成
        self.eval_density = tkk.Label(self.evalFrm)
        self.eval_density.configure(text="密集度　：",font=("",40),foreground="black", background="white")
        self.eval_density.pack(anchor="w")
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
        # VideoCaptureクラスのget_frameで画像を取得
        try:
            ret, frame = self.cap.get_frame()
        # 取得できなかったら
        except:
            ret = False
            frame = 0
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            #cam1_canvasに映像表示
            self.movie_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # 100ミリ秒ごとにupdate関数を実行
        self.after(100, self.update)
        
        
        
        
# 動画取得用のクラスを作成
class VideoCapture:
    def __init__(self):
        # カメラ読み込み
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print('カメラを読み込めませんでした。')
                
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
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # 画像読込失敗：False・Noneを返す
            else:
                return (ret, None)
        else:
            return (ret, None)
        

if __name__ == "__main__":
    app = CovidApp()
    app.mainloop()