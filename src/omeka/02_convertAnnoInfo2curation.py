# -*- coding: utf-8 -*-
import urllib.request, json
from bs4 import BeautifulSoup
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace
from hashlib import md5
import sys
import argparse


def parse_args(args=sys.argv[1:]):
    """ Get the parsed arguments specified on this script.
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'omeka_instance',
        action='store',
        type=str,
        help='omeka instance')

    return parser.parse_args(args)


def make_md5(s):
    return md5(s.encode('utf-8')).hexdigest()


def getInfoFromManifest(url):
    response = urllib.request.urlopen(url)
    response_body = response.read().decode("utf-8")
    data = json.loads(response_body.split('\n')[0])

    anno_list_url = data["sequences"][0]["canvases"][0]["otherContent"][0]["@id"];

    image_url = data["sequences"][0]["canvases"][0]["images"][0]["resource"]["service"]["@id"];
    image_url = image_url + "/full/600,/0/default.jpg"

    original_manifest = data["sequences"][0]["canvases"][0]["metadata"][0]["value"];
    source_manifest = collection_manifest.replace("http://", "https://")
    label = data["label"]

    response = urllib.request.urlopen(anno_list_url)
    response_body = response.read().decode("utf-8")
    data = json.loads(response_body.split('\n')[0])

    resources = data["resources"]

    for i in range(len(resources)):
        resource = resources[i]
        text = resource["resource"][0]["chars"]
        text = BeautifulSoup(text, "lxml").text

        o_name = text

        selector = resource["on"][0]["selector"]["default"]["value"]

        id = resource["@id"]

        canvas_id = resource["on"][0]["full"]

        manfiest = resource["on"][0]["within"]["@id"]

        if o_name not in all:
            all[o_name] = {}
            tmp = all[o_name]
            tmp["member"] = {}
            tmp["manifest"] = source_manifest
            tmp["label"] = label

        obj = {}
        all[o_name]["member"][canvas_id] = canvas_id + "#" + selector


flg = True
page = 1

g = Graph()

args = parse_args()
ins = args.omeka_instance

outputPath = "data/" + ins + ".rdf"

all = {}

while flg:
    url = "http://diyhistory.org/uparl/" + ins + "/api/items?item_type=18&page=" + str(page)
    print(url)

    print(page)

    page += 1

    response = urllib.request.urlopen(url)
    response_body = response.read().decode("utf-8")
    data = json.loads(response_body.split('\n')[0])

    if len(data) > 0:
        for i in range(len(data)):
            obj = data[i]

            element_texts = obj["element_texts"]
            for e in element_texts:
                if e["element"]["name"] == "On Canvas":
                    uuid = e["text"]

                    tmp_url = "http://diyhistory.org/uparl/" + ins + "/api/items?search=" + uuid

                    response = urllib.request.urlopen(tmp_url)
                    response_body = response.read().decode("utf-8")
                    data_t = json.loads(response_body.split('\n')[0])

                    obj_t = data_t[0]
                    id = obj_t["id"]
                    collection_id = obj_t["collection"]["id"]

            manifest = "https://diyhistory.org/uparl/" + ins + "/oa/items/" + str(id) + "/manifest.json"

            collection_manifest = "http://diyhistory.org/uparl/" + ins + "/oa/collections/" + str(
                collection_id) + "/manifest.json"

            getInfoFromManifest(manifest)

    else:
        flg = False

for o_name in all:
    with open('data/template.json') as f:
        df = json.load(f)

    df["@id"] = "https://nakamura196.github.io/narita/json/" + make_md5(o_name) + ".json"
    df["selections"] = []

    selection = {}
    df["selections"].append(selection)

    selection["@id"] = df["@id"] + "/range" + str(1)
    selection["@type"] = "sc:Range"
    selection["label"] = "Manual curation by IIIF Curation Viewer"

    selection["members"] = []

    manifest = {}
    selection["within"] = manifest
    manifest["@id"] = all[o_name]["manifest"]
    manifest["@type"] = "sc:Manifest"
    manifest["@label"] = all[o_name]["label"]

    members = all[o_name]["member"]
    count = 1
    for key in sorted(members):
        member = {}

        selection["members"].append(member)

        member["@id"] = members[key]
        member["@type"] = "sc:Canvas"
        member["label"] = key

        count += 1

    # print(df)

    with open("../../docs/json/" + make_md5(o_name) + ".json", 'w') as outfile:
        json.dump(df, outfile, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

    text = o_name

    if len(text.split("-")) != 3:
        continue

    organization = text.split("@")[1]
    id = text.split("@")[0]
    # edition = text.split("#")[0]
    # text = text.split("#")[1].split("@")[0]

    subject = "http://example.org/resource/" + text
    subject = URIRef(subject)
    g.add(
        (subject, URIRef("http://example.org/property/differentEdition"), URIRef("http://example.org/resource/" + id)))

    g.add((subject, URIRef("http://example.org/property/organization"), Literal(organization)))

    # anno_uri = URIRef(id)
    g.add((subject, URIRef("http://example.org/property/curation"), URIRef(df["@id"])))

g.serialize(destination=outputPath)
