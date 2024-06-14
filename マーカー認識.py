import time
import cv2
from cv2 import aruco
import math
import numpy as np
import keyboard
import os
import pandas as pd

def calculate_distance(pt1, pt2, marker_length_pixel):
    pixel_distance = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)  # ピクセル単位の距離
    actual_distance_cm = (marker_length / marker_length_pixel) * pixel_distance  # ピクセルからセンチメートルに変換
    return actual_distance_cm

# ArUcoマーカーを検出し、マーカー中心点の座標と長さを取得する関数
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


# カメラのセットアップ(anker)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # カメラを開く
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # フレーム幅を設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # フレーム高さを設定
cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
cap.set(cv2.CAP_PROP_FOCUS, 0)  # フォーカスを設定
cap.set(cv2.CAP_PROP_ZOOM, 100)  # ズームを設定
cap.set(cv2.CAP_PROP_BRIGHTNESS, 80)  # 明るさを設定
cap.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定
# ArUcoのパラメータを設定
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  # ArUco辞書を取得
aruco_params = aruco.DetectorParameters()  # ArUcoの検出パラメータを設定


# マーカーの1辺の長さをユーザに入力させる
marker_length = float(input("マーカーの1辺の長さ（センチメートル）を入力してください："))
# 固定マーカーと動くマーカーのIDを定義
fixed_marker_id = 0 # 固定されているマーカーのID
movable_marker_ids = [1, 2]  # 動くマーカーのIDリスト

date = time.strftime("%Y%m%d_%H_%M_%S")  # 現在の日時を取得
start_time = time.time()  # 開始時間を記録
metadata = []


while True:
    #マーカー検出用カメラ処理

    key = cv2.waitKey(1)  # キー入力を待つウインドウ表示用実験の際は不要
    ret, img = cap.read()  # ankerのカメラから画像を取得
    current_time = time.time() - start_time


#エラーが発生するかもしれない項をtryにぶち込む
    try:
        # ArUcoマーカーの検出と座標の取得
        marker_centers, marker_lengths, img = detect_aruco_markers(img)

        # 固定マーカーの座標と長さを取得
        fixed_marker_center = marker_centers.get(fixed_marker_id)
        fixed_marker_length = marker_lengths.get(fixed_marker_id)

        # 動くマーカーの座標と距離の計算
        movable_marker_distances = [] #空のリストを作る
        movable_marker_centers = [marker_centers.get(marker_id, None) for marker_id in movable_marker_ids]
        for i, marker_id in enumerate(movable_marker_ids):
            movable_marker_center = marker_centers.get(marker_id)
            movable_marker_length = marker_lengths.get(marker_id)
            if fixed_marker_center and movable_marker_center and fixed_marker_length and movable_marker_length:
                distance_cm = calculate_distance(fixed_marker_center, movable_marker_center, movable_marker_length)
                movable_marker_distances.append(distance_cm)

                # 固定点と移動点の中心を線で結ぶ（0番目の動くマーカーは青色、1番目は赤色）
                line_color = (0, 255, 255) if i == 0 else (0, 0, 255)
                cv2.line(img, fixed_marker_center, movable_marker_center, line_color, 2)


        ## リストにデータ追加
        #metadata.append([current_time] +
        #                movable_marker_distances +
        #                [fixed_marker_center[0], fixed_marker_center[1]] +  # X座標とY座標に分ける
        #                [movable_marker_centers[0][0], movable_marker_centers[0][1],
        #                 movable_marker_centers[1][0], movable_marker_centers[1][1]] +  # X座標とY座標に分ける
        #                [fixed_marker_length])






        cv2.imshow('Wed_Camera', img)  # 画像を表示





    except Exception as e:
        print("Errorが発生しました:", e)

    if keyboard.is_pressed("q"):  # qが押されたら終了
        #fg.exit()
        break


print("実験終了データを保存します")

# 結果をCファイルに保存
df = pd.DataFrame(metadata, columns=["Time(S)"] +
                                    [f"{i + 1}Distance_Marker(cm)" for i in range(len(movable_marker_ids))] +
                                    ["Fixed_Marker_Center_X", "Fixed_Marker_Center_Y"] +
                                    ["Movable_Marker_Center_1_X", "Movable_Marker_Center_1_Y",
                                     "Movable_Marker_Center_2_X", "Movable_Marker_Center_2_Y"] +
                                    ["fixed_marker_length"])



output_dir = "save_data/experiment" + str(date)
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, f"experiment{date}.xlsx")
df.to_excel(excel_path, index=False)
print("実験終了")

# ウィンドウを閉じる
cv2.destroyAllWindows()