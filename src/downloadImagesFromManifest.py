import json
import sys
import argparse
import json
import urllib.request

def parse_args(args=sys.argv[1:]):
    """ Get the parsed arguments specified on this script.
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'url_to_manifest',
        action='store',
        type=str,
        help='url to manifest file.')

    parser.add_argument(
        'path_to_dir',
        action='store',
        type=str,
        help='full path to output dir.')

    return parser.parse_args(args)

def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(e)

def main(url_to_manifest, path_to_dir):

    res = urllib.request.urlopen(url_to_manifest)
    data = json.loads(res.read().decode('utf-8'))

    canvases = data["sequences"][0]["canvases"]
    for i in range(0, len(canvases)):
        canvas = canvases[i]

        img_url = canvas["images"][0]["resource"]["@id"]
        img_url = img_url.replace("full/full", "full/,600")
        filename = img_url.split("/")[7].replace(".tif", ".jpg")

        print(str(i)+"/"+str(len(canvases))+"\t"+filename)

        download_image(img_url, path_to_dir+"/"+filename)

if __name__ == "__main__":
    args = parse_args()

    main(
        args.url_to_manifest,
        args.path_to_dir)
