import time
import cv2
from cv2 import aruco
#import opencv-cont
import math
import numpy as np
import keyboard
import os
import pandas as pd

def AR_detect(src):
    src = np.array(src)
    # ARマーカー認識#################################################################################
    corners, ids, rejectedImgPoints = aruco.detectMarkers(src, dict_aruco, parameters=parameters)

    list_ids = np.ravel(ids)
    num_id = 303  # ARタグのナンバー
    if num_id in np.ravel(ids):
        index = np.where(ids == num_id)[0][0]  # num_id が格納されているindexを抽出
        cornerUL = corners[index][0][0]
        cornerUR = corners[index][0][1]
        cornerBR = corners[index][0][2]
        cornerBL = corners[index][0][3]

        center = [(cornerUL[0] + cornerBR[0]) / 2, (cornerUL[1] + cornerBR[1]) / 2]

        print('左上 : {}'.format(cornerUL))
        print('右上 : {}'.format(cornerUR))
        print('右下 : {}'.format(cornerBR))
        print('左下 : {}'.format(cornerBL))
        print('中心 : {}'.format(center))
        distance = math.sqrt((cornerUR[0] - cornerUL[0]) ** 2 + (cornerUR[1] - cornerUL[1]) ** 2)
        print(distance)
       # wid.append((distance))
    np.seterr(divide = "ignore")  #90度の際のエラーを無視可能にする
    atan = math.atan((cornerUR[1] - cornerUL[1])/(cornerUR[0] - cornerUL[0]))
    print(math.degrees(atan))

    # ARマーカーの中心座標
    cx = int(center[0])
    cy = int(center[1])
    pt = (cx, cy)

    # ARマーカー
    dst = aruco.drawDetectedMarkers(src, corners, ids)
    cv2.imshow("test dst",dst)
    AR_drow.append(dst)
    #print(dst)

    return dst, pt, AR_drow


if __name__ == '__main__':
    date = time.strftime("%Y%m%d_%H_%M_%S")


    #使用するカメラのセットアップ
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # カメラを開く
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # フレーム幅を設定
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)  # フレーム高さを設定
    cap.set(cv2.CAP_PROP_FPS, 60)  # FPSを設定
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカスをオフ
    cap.set(cv2.CAP_PROP_FOCUS, 0)  # フォーカスを設定
    cap.set(cv2.CAP_PROP_ZOOM, 100)  # ズームを設定
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 80)  # 明るさを設定
    cap.set(cv2.CAP_PROP_TILT, -10)  # 傾きを設定
    cap.set(cv2.CAP_PROP_PAN, 0)  # パンを設定

    #変更する場合、下記のコマンドを有効にすると便利
    #cap.set(cv2.CAP_PROP_SETTINGS, 1) #カメラの設定値を変更する際に使用

    #パラメータ
    dict_aruco = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
    parameters = aruco.DetectorParameters()

    #保存用
    pt_list = []
    img_list = []
    AR_drow = []

    while True:
        key = cv2.waitKey(1)
        ret, img = cap.read()
        cv2.imshow('Wed_Camera', img)
        img_list.append(img)
        try:
            dst, pt, AR_drow = AR_detect(img)
            print(dst)
            pt_list.append(pt)
            #AR_drow.append(dst)
        except:
            i = 0

        if keyboard.is_pressed("q"):
            break

    os.makedirs("save_data/AR_test" + str(date) + "/img")
    for i in range(len(img_list)):
        pic_path0 = "save_data/AR_test" + str(date) + "/img/img" + str(i) + ".jpg"
        cv2.imwrite(pic_path0, img_list[i])
    print(len(AR_drow))
    os.makedirs("save_data/AR_test" + str(date) + "/AR_drow")
    for i in range(len(AR_drow)):
        pic_path0 = "save_data/AR_test" + str(date) + "/AR_drow/AR_drow" + str(i) + ".jpg"
        cv2.imwrite(pic_path0, AR_drow[i])

    dict = {"AR_maker":pt_list}
    df = pd.DataFrame(dict)
    df.to_csv("save_data/AR_test" + str(date) + "/AR_center.csv")
    print("実験終了")