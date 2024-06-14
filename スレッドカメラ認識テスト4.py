# OpenCV、NumPy、その他必要なライブラリをインポート
import time
import cv2
from cv2 import aruco
import math
import numpy as np
import keyboard
import os
import pandas as pd
from myForceGauge import ForceGauge_communication
import myDynamixel
import threading
import queue
import sys

# カメラのセットアップ(anker)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # カメラを開く
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # フレーム幅を設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # フレーム高さを設定
cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
cap.set(cv2.CAP_PROP_FOCUS, 0)  # フォーカスを設定
cap.set(cv2.CAP_PROP_ZOOM, 100)  # ズームを設定
cap.set(cv2.CAP_PROP_BRIGHTNESS, 80)  # 明るさを設定
cap.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定


def get_camera_capture():
    i = 0
    x2 = time.time()
    global frame, x, metadata, img_file
    while True:
        # カメラ画像の取得
        x1 = time.time()  # 現在の時間を記録

        if i > 0:
            t1 = x1 - x2  # 前回のループからの経過時間を計算
            fps = 1 / t1
            print(fps)

        x2 = time.time()  # 現在の時間を次回のために保存

        i += 1  # iを加算

        ret, frame = cap.read()
        img_file.append(frame.copy())
        #cv2.imshow("frame", frame)

        if x == "f":
            break


# 画像取り込みスレッドの作成
thread = threading.Thread(target=get_camera_capture, daemon=True)
thread.start()
x = "r"
img_file = []
metadata = []
date = time.strftime("%Y%m%d_%H_%M_%S")  # 現在の日時を取得
start_time = time.time()  # 開始時間を記録

frame = None
while frame is None:
    print("Noneループが回ってます")

time.sleep(1)
print("q")

while True:
    current_time = start_time - time.time()
    metadata.append(current_time)


    if keyboard.is_pressed("q"):  # qが押されたら終了
        break

x = "f"

# 結果をCファイルに保存
df = pd.DataFrame(metadata, columns=["Time(S)"])

os.makedirs("save_data/AR_test" + str(date))
for i in range(len(img_file)):
    pic_path0 = "save_data/AR_test" + str(date) + "/img" + str(i) + ".jpg"
    cv2.imwrite(pic_path0, img_file[i])

output_dir = "save_data/experiment" + str(date)
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, f"experiment{date}_queueSize.xlsx")
df.to_excel(excel_path, index=False)
print("実験終了")

# ウィンドウを閉じる
cv2.destroyAllWindows()

sys.exit()
