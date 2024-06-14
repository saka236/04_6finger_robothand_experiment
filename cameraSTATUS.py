import cv2


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_SETTINGS, 1) #カメラの設定値を変更する際に使用

while True:
    key = cv2.waitKey(1)
    ret, img = cap.read()
    cv2.imshow('Wed_Camera', img)
#def check_info(last_index):
#    for i in range(last_index):
#        try:
#            cap = cv2.VideoCapture(i)
#            if cap is None or not cap.isOpened():
#                raise ConnectionError
#            fps = cap.get(cv2.CAP_PROP_FPS)
#            print(f"-*- DEVICE_ID: {i} -*-")
#            contrast = cap.get(cv2.CAP_PROP_CONTRAST)
#            saturation = cap.get(cv2.CAP_PROP_SATURATION)
#            gamma = cap.get(cv2.CAP_PROP_GAMMA)
#            print(f"FPS: {fps}")
#            print(f"Contrast: {contrast}")
#            print(f"Saturation: {saturation}")
#            print(f"gamma: {gamma}")
#        except ConnectionError:
#            break
#
#
#if __name__ == "__main__":
#    check_info(10)