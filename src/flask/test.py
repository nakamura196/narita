import json
import csv
import urllib.request
import argparse
import requests
import shutil
import os
import sys
import os  # osモジュールのインポート
import numpy as np
import cv2


def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


# 特徴抽出機の生成
# detector = cv2.xfeatures2d.SIFT_create()
detector = cv2.AKAZE_create()

input_url = "https://iiif.dl.itc.u-tokyo.ac.jp/repo/iiif-img/168120/1987,809,3875,4769/,600/0/default.jpg"
download_img(input_url, "data/input.jpg")

img1 = cv2.imread("data/input.jpg", 0)

# kpは特徴的な点の位置 destは特徴を現すベクトル
kp1, des1 = detector.detectAndCompute(img1, None)

url = "https://www.dl.ndl.go.jp/api/iiif/2553035/manifest.json"
res = urllib.request.urlopen(url)
# json_loads() でPythonオブジェクトに変換
data = json.loads(res.read().decode('utf-8'))

canvases = data["sequences"][0]["canvases"]

for i in range(0, len(canvases)):
    canvas = canvases[i]
    img_url = canvas["images"][0]["resource"]["service"]["@id"] + "/full/,600/0/default.jpg"

    download_img(img_url, "data/tmp.jpg")

    img2 = cv2.imread("data/tmp.jpg", 0)

    kp2, des2 = detector.detectAndCompute(img2, None)
    # 特徴点の比較機
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    # 割合試験を適用
    good = []
    match_param = 0.6
    for m, n in matches:
        if m.distance < match_param * n.distance:
            good.append([m])

    print(str(i + 1) + "：" + str(len(good)))

    if len(good) > 0:
        # cv2.drawMatchesKnnは適合している点を結ぶ画像を生成する
        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
        cv2.imwrite("data/" + str(len(good)) + "_" + str(i + 1) + ".png", img3)
