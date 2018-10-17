import os
import io
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename

import json
import csv
import urllib.request
import argparse
import requests
import shutil
import sys
import numpy as np
import cv2
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 640
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)


@app.route('/')
def index():
    return render_template('index.html')


from flask import json


def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


@app.route('/find', methods=['GET', 'POST'])
def find():
    result = {}
    result["array"] = []

    if request.method == 'GET':

        # 特徴抽出機の生成
        # detector = cv2.xfeatures2d.SIFT_create()
        detector = cv2.AKAZE_create()

        input_url = request.args.get("img_url")
        result["img_url"] = input_url
        download_img(input_url, "data/input.jpg")

        img1 = cv2.imread("data/input.jpg", 0)

        # kpは特徴的な点の位置 destは特徴を現すベクトル
        kp1, des1 = detector.detectAndCompute(img1, None)

        url = request.args.get("manifest")
        result["manifest"] = url
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

            obj = {}
            obj["score"] = len(good)

            print(str(i + 1) + "/" + str(len(canvases)) + "\t" +str(len(good)))

            if len(good) > 1:
                # cv2.drawMatchesKnnは適合している点を結ぶ画像を生成する
                img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)

                filename = str(uuid.uuid1()) + ".png"

                output_img_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                cv2.imwrite(output_img_url, img3)

                obj["img"] = "http://localhost:5000/data/" + filename

            result["array"].append(obj)

    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/data/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.debug = True
    app.run()
