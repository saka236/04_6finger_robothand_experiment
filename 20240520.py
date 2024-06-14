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


# -----関数定義-------
# 2つの座標間の距離をセンチメートル単位で計算する関数
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


def check_brightness(img1):
    # 画像の平均輝度値を計算
    mean_brightness = np.mean(img1)

    # 閾値を設定(暗いと判断する輝度値)　ピクセルの輝度　０から255
    brightness_threshold = 30

    # 平均輝度値が閾値より小さければ真っ暗と判断
    if mean_brightness < brightness_threshold:
        return False  # 暗い
    else:
        return True  # 明るい

#-------関数定義終わり------------------------------------------------------------------------------------------------------



#フォースゲージとカメラの初期セットアップ

#フォースゲージ関連の動作
fg = ForceGauge_communication()  # インスタンス化
fg.init('COM3')
# カメラのセットアップ(anker)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # カメラを開く
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # フレーム幅を設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)  # フレーム高さを設定
cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
cap.set(cv2.CAP_PROP_FOCUS, 60)  # フォーカスを設定
cap.set(cv2.CAP_PROP_ZOOM, 176)  # ズームを設定
cap.set(cv2.CAP_PROP_BRIGHTNESS, 80)  # 明るさを設定
cap.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定
# カメラのセットアップ(ハンド内)
cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # カメラを開く
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # フレーム幅を設定
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)  # フレーム高さを設定
cap1.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
cap1.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オート フォーカスをオフ
cap1.set(cv2.CAP_PROP_FOCUS, 60)  # フォーカスを設定
cap1.set(cv2.CAP_PROP_ZOOM, 176)  # ズームを設定
#cap1.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 明るさを設定
cap1.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
cap1.set(cv2.CAP_PROP_PAN, 0)  # パンを設定
# ArUcoのパラメータを設定
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  # ArUco辞書を取得
aruco_params = aruco.DetectorParameters()  # ArUcoの検出パラメータを設定
# 保存用のリストを初期化
metadata = []
handspeed = 100

# dynamixel初期設定
dxl = myDynamixel.Dxlfunc()  # インスタンス化
MotorNum = dxl.init('COM4', baudrate=4000000)  # COM通信容量を指定
print(MotorNum)

if MotorNum > 0:
    print("dynamixel初期化成功")
else:
    print("初期化失敗")
Motor_ID = 1  # モーターIDを設定

dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)  # モーターのトルクをオフにする(初期化)
dxl.write(Motor_ID, dxl.Address.TorqueEnable, True)  # モーターのトルクをオンにする

dxl.Change_OperatingMode(Motor_ID, dxl.operating_mode.velocity_control)  # モーターを速度コントロール

print("キャリブレーションを実施")
dxl.write(Motor_ID, dxl.Address.GoalVelocity, -handspeed)  # 外側のハンドをハンドを閉じる(初期化)

while True:
    current = dxl.read(Motor_ID, dxl.Address.PresentCurrent)  # トルク読み取り
    # print(current)
    if current < -600:
        print("外爪が閉じました")
        dxl.write(Motor_ID, dxl.Address.GoalVelocity, 0)
        break

    elif keyboard.is_pressed("q"):  # 3を押すとハンドを開いてプログラムを終了
        dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)
        break

dxl.write(Motor_ID, dxl.Address.GoalVelocity, handspeed)  # 内側のハンドをハンドを閉じる(初期化)

while True:
    ret1, img1 = cap1.read()
    bright_check = check_brightness(img1)

    if not bright_check:
        dxl.write(Motor_ID, dxl.Address.GoalVelocity, 0)
        print("内爪が閉じました")
        all_hand_close_posision = dxl.read(Motor_ID, dxl.Address.PresentPosition)
        break
    elif keyboard.is_pressed("q"):  # 3を押すとハンドを開いてプログラムを終了
        dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)
        break
all_hand_close_pos = dxl.read(Motor_ID, dxl.Address.PresentPosition)

time.sleep(0.5)

print("外爪を開いて距離を取得します")
dxl.write(Motor_ID, dxl.Address.GoalVelocity, handspeed)  # 外側のハンドをハンドを開く(初期化)

while True:
    current = dxl.read(Motor_ID, dxl.Address.PresentCurrent)  # トルク読み取り
    if current > 600:
        print("外爪が開きました")
        dxl.write(Motor_ID, dxl.Address.GoalVelocity, 0)
        break
    elif keyboard.is_pressed("q"):  # 3を押すとハンドを開いてプログラムを終了
        dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)
        break

outer_hand_open_pos = dxl.read(Motor_ID, dxl.Address.PresentPosition)

outer_finger_dis = outer_hand_open_pos - all_hand_close_pos
print(f"外爪の開閉移動距離は{outer_finger_dis}です" )
print("初期位置に移行")
#再度初期位置に移行

dxl.write(Motor_ID, dxl.Address.GoalVelocity, -handspeed)  # 外側のハンドをハンドを閉じる(初期化)

while True:
    current = dxl.read(Motor_ID, dxl.Address.PresentCurrent)  # トルク読み取り
    if current < -600:
        print("外爪が閉じました")
        dxl.write(Motor_ID, dxl.Address.GoalVelocity, 0)
        break

    elif keyboard.is_pressed("q"):  # 3を押すとハンドを開いてプログラムを終了
        dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)
        break

time.sleep(1)
key = cv2.waitKey(1)
dxl.write(Motor_ID, dxl.Address.GoalVelocity, handspeed)  # 内側のハンドをハンドを閉じる(初期化)

ret1, img1 = cap1.read() #img1をリセット
inner_finger_open_position = dxl.read(Motor_ID, dxl.Address.PresentPosition)
while True:
    ret1, img1 = cap1.read()
    bright_check = check_brightness(img1)

    if not bright_check:
        dxl.write(Motor_ID, dxl.Address.GoalVelocity, 0)
        print("内爪が閉じました")
        break
    elif keyboard.is_pressed("q"):  # 3を押すとハンドを開いてプログラムを終了
        dxl.write(Motor_ID, dxl.Address.TorqueEnable, False)
        break
inner_finger_close_position = dxl.read(Motor_ID, dxl.Address.PresentPosition)
inner_finger_dis = inner_finger_close_position - inner_finger_open_position
print(f"内爪の開閉移動距離は{inner_finger_dis}です" )

ret1, img1 = cap1.read() #img1をリセット
print("初期セットアップ完了") #--------------------------------------------------------------------------------------------------------------------

# マーカーの1辺の長さをユーザに入力させる
marker_length = float(input("マーカーの1辺の長さ（センチメートル）を入力してください："))
# 固定マーカーと動くマーカーのIDを定義
FIXED_MARKER_ID = 0  # 固定されているマーカーのID
movable_marker_ids = [1, 2]  # 動くマーカーのIDリスト

date = time.strftime("%Y%m%d_%H_%M_%S")  # 現在の日時を取得
start_time = time.time()  # 開始時間を記録

#カメラ動作,フォースゲージ動作,リストにデータを追加　メインの動作部分

while True:
    #マーカー検出用カメラ処理

    key = cv2.waitKey(1)  # キー入力を待つウインドウ表示用実験の際は不要
    ret, img = cap.read()  # ankerのカメラから画像を取得
    ret1, img1 = cap1.read() #　inHANDのカメラから画像を取得
    bright_check = check_brightness(img1)


    if not bright_check:
        # 真っ暗の場合、モーターの動きを変更
        print("暗い環境が検出されました。モーターの動きを変更します。")

#エラーが発生するかもしれない項をtryにぶち込む
    try:
        # ArUcoマーカーの検出と座標の取得
        marker_centers, marker_lengths, img = detect_aruco_markers(img)

        # 固定マーカーの座標と長さを取得
        fixed_marker_center = marker_centers.get(FIXED_MARKER_ID)
        fixed_marker_length = marker_lengths.get(FIXED_MARKER_ID)

        # 動くマーカーの座標と距離の計算
        movable_marker_distances = []
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

                # 計算した距離を保存
                current_time = time.time() - start_time  # 現在の経過時間
                current = dxl.read(Motor_ID, dxl.Address.PresentCurrent)
                # リストにデータ追加
                metadata.append([current_time] +
                                movable_marker_distances +
                                [fixed_marker_center] +
                                movable_marker_centers +
                                [fixed_marker_length] +
                                [fg.read()] +
                                [current])
                cv2.imshow('Wed_Camera', img)  # 画像を表示
                cv2.imshow('inHand_Camera', img1)




    except Exception as e:
        print("Errorが発生しました:", e)

    if keyboard.is_pressed("q"):  # qが押されたら終了
        fg.exit()
        break

# 結果をCファイルに保存

df = pd.DataFrame(metadata, columns=["Time(S)"] +
                                    [f"{i + 1}Distance_Marker(cm)" for i in range(len(movable_marker_ids))]  +
                                    ["Fixed_Marker_Center"] +  # 固定マーカーの座標の列名
                                    [f"{i + 1}Movable_Marker_Center" for i in range(len(movable_marker_ids))] +
                                    ["fixed_marker_length"] +
                                    ["Force(N)"] +
                                    ["current"])

output_dir = "save_data/experiment" + str(date)
os.makedirs(output_dir, exist_ok=True)
excel_path = os.path.join(output_dir, "experiment.xlsx")
df.to_excel(excel_path, index=False)
print("実験終了")

# ウィンドウを閉じる
cv2.destroyAllWindows()