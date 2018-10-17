import json
import urllib.request
import pandas as pd
import openpyxl
import csv
import uuid

inputs = []
input_csv_path = "csv/input.csv"

# input_url = ""

with open(input_csv_path, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        if len(row) > 0 and row[0] != "":
            inputs.append(row[0])

manifests = []

input_file = "csv/test2.csv"

with open(input_file, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        if len(row) > 0 and row[0] != "":
            manifests.append(row[0])

table = []
row = ["input", "manifest", "page", "score", "img"]
table.append(row)

for input_url in inputs:

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

df = pd.DataFrame(table)

df.to_excel(input_file + "_" + str(uuid.uuid1()) + ".xlsx", index=False, header=False)
