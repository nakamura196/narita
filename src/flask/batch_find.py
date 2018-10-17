import json
import urllib.request
import pandas as pd
import openpyxl

input_url = "https://iiif.dl.itc.u-tokyo.ac.jp/repo/iiif-img/168120/1987,809,3875,4769/,600/0/default.jpg"

manifests = ["https://www.dl.ndl.go.jp/api/iiif/2553033/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553034/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553035/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553036/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553037/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553038/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553039/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553040/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553041/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553042/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553043/manifest.json",
             "https://www.dl.ndl.go.jp/api/iiif/2553044/manifest.json"]

table = []
row = ["input", "manifest", "page", "score", "img"]
table.append(row)

for i in range(len(manifests)):

    print(str(i + 1) + "/" + str(len(manifests)))

    manifest = manifests[i]

    url = "http://localhost:5000/find?img_url=" + input_url + "&manifest=" + manifest

    res = urllib.request.urlopen(url)
    # json_loads() でPythonオブジェクトに変換
    data = json.loads(res.read().decode('utf-8'))

    row = []
    arr = data["array"]
    for j in range(len(arr)):
        obj = arr[j]
        img = ""
        if "img" in obj:
            img = obj["img"]
        row = [data["img_url"], data["manifest"], str(j + 1), obj["score"], img]
        table.append(row)

df = pd.DataFrame(table);

df.to_excel("data/result.xlsx", index=False, header=False)
