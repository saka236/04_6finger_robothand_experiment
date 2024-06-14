# OpenCV、NumPy、その他必要なライブラリをインポート
import time
import cv2
from cv2 import aruco
import math
import numpy as np
import keyboard
import os
import pandas as pd
import myDynamixel
import threading
import queue
import sys

# カメラのセットアップ(anker)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # カメラを開く
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280-1)  # フレーム幅を設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720-1)  # フレーム高さを設定
cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
cap.set(cv2.CAP_PROP_FOCUS, 0)  # フォーカスを設定
cap.set(cv2.CAP_PROP_ZOOM, 25)  # ズームを設定
cap.set(cv2.CAP_PROP_BRIGHTNESS, 25)  # 明るさを設定
cap.set(cv2.CAP_PROP_TILT, 0)  # 傾きを設定
cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定

i = 0
x2 = time.time()
while True:
    # カメラ画像の取得
    x1 = time.time()  # 現在の時間を記録

    if i > 5:
        t1 = x1 - x2  # 前回のループからの経過時間を計算
        fps = 1 / t1
        print(fps)

    x2 = time.time()  # 現在の時間を次回のために保存

    i += 1  # iを加算

    ret, frame = cap.read()
    cv2.imshow("frame",frame)
    #cv2.imshow("frame", frame)
    if keyboard.is_pressed("q"):  # qが押されたら終了
        cv2.destroyAllWindows()
        break

sys.exit()