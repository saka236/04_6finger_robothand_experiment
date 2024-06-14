
from cv2 import aruco
import math
import numpy as np
import threading
import queue
import time
import keyboard
import cv2
import pandas as pd
import os


# ArUcoのパラメータを設定
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  # ArUco辞書を取得
aruco_params = aruco.DetectorParameters()  # ArUcoの検出パラメータを設定
# カメラを開く
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # カメラを開く
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # フレーム幅を設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # フレーム高さを設定
cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
cap.set(cv2.CAP_PROP_FOCUS, 10)  # フォーカスを設定
cap.set(cv2.CAP_PROP_ZOOM, 100)  # ズームを設定
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)  # 明るさを設定
cap.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定

# フレーム共用のキュー
queue_size = 1

q_frames = queue.Queue(queue_size)

def frame_update():
    '''画像取込'''
    while True:
        # カメラ画像の取得
        # _, frame = cap.read()
        ret, frame1 = cap.read()
        frame = frame1[180:640, 320:760]
        # 取得した画像をキューに追加
        q_frames.put(frame)


def detect_aruco_markers(image):
    # ArUcoマーカーを検出
    corners, ids, _ = aruco.detectMarkers(image, aruco_dict, parameters=aruco_params)

    marker_centers = {}
    marker_lengths = {}
    if ids is not None:
        for i, marker_id in enumerate(np.ravel(ids)):
            index = np.where(ids == marker_id)[0][0]
            corner_ul = corners[index][0][0]
            corner_br = corners[index][0][2]
            corner_ur = corners[index][0][1]
            center = [(corner_ul[0] + corner_br[0]) / 2, (corner_ul[1] + corner_br[1]) / 2]
            marker_length_pixel = math.sqrt((corner_ul[0] - corner_ur[0]) ** 2 + (corner_ul[1] - corner_ur[1]) ** 2)
            marker_centers[marker_id] = (int(center[0]), int(center[1]))  # 座標を整数に変換
            marker_lengths[marker_id] = marker_length_pixel

    # 検出されたマーカーを別ウィンドウで表示
    aruco.drawDetectedMarkers(image, corners, ids)

    return marker_centers, marker_lengths, image  # 画像を返すように変更

# 画像取り込みスレッドの作成
thread = threading.Thread(target=frame_update, daemon=True)
# スレッドの開始
thread.start()

metadata = []
date = time.strftime("%Y%m%d_%H_%M_%S")  # 現在の日時を取得


start_time = time.time()  # 開始時間を記録

print("main loop start")
# 画像表示用スレッド
while True:
    frame = q_frames.get()

    marker_centers, marker_lengths, img = detect_aruco_markers(frame)
    cv2.imshow("Image", img)
    current_time = time.time() - start_time
    metadata.append([current_time]+[marker_centers])

    # キーを押すとループを終了する
    if keyboard.is_pressed("q"):  # qが押されたら終了
        break

df = pd.DataFrame(metadata, columns=["Time(S)"]+["マーカーセンター"])



output_dir = "save_data/with_queue_experiment_test" + str(date)
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, f"experiment{date}_queueSize.xlsx")
df.to_excel(excel_path, index=False)
print("実験終了")

# カメラを閉じる
cap.release()
# すべてのウィンドウを閉じる
cv2.destroyAllWindows()