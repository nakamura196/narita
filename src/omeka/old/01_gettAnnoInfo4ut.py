# -*- coding: utf-8 -*-
import urllib.request, json
from bs4 import BeautifulSoup
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace


def getInfoFromManifest(url):
    response = urllib.request.urlopen(url)
    response_body = response.read().decode("utf-8")
    data = json.loads(response_body.split('\n')[0])

    anno_list_url = data["sequences"][0]["canvases"][0]["otherContent"][0]["@id"];

    image_url = data["sequences"][0]["canvases"][0]["images"][0]["resource"]["service"]["@id"];
    image_url = image_url + "/full/600,/0/default.jpg"

    # source_manifest = data["sequences"][0]["canvases"][0]["metadata"][0]["value"];
    source_manifest = collection_manifest

    response = urllib.request.urlopen(anno_list_url)
    response_body = response.read().decode("utf-8")
    data = json.loads(response_body.split('\n')[0])

    resources = data["resources"]

    for i in range(len(resources)):
        resource = resources[i]
        text = resource["resource"][0]["chars"]
        text = BeautifulSoup(text, "lxml").text

        organization = text.split("@")[1]
        edition = text.split("#")[0]
        text = text.split("#")[1].split("@")[0]

        selector = resource["on"][0]["selector"]["default"]["value"]

        id = resource["@id"]

        canvas_id = resource["on"][0]["full"]

        manfiest = resource["on"][0]["within"]["@id"]

        subject = "http://ja.dbpedia.org/resource/" + edition + "#" + text + "@" + organization
        subject = URIRef(subject)
        g.add((subject, URIRef("http://example.org/property/differentEdition"),
               URIRef("http://ja.dbpedia.org/resource/" + edition + "#" + text)))

        g.add((subject, URIRef("http://example.org/property/organization"), Literal(organization)))

        anno_uri = URIRef(id)
        g.add((subject, URIRef("http://example.org/property/anno"), anno_uri))

        g.add((anno_uri, URIRef("http://example.org/property/canvas"), URIRef(canvas_id)))
        g.add((anno_uri, URIRef("http://example.org/property/selector"), Literal(selector.split("=")[1])))
        g.add((anno_uri, FOAF.thumbnail, URIRef(image_url)))
        g.add((anno_uri, URIRef("http://example.org/property/manifest"), URIRef(source_manifest)))


flg = True
page = 1

g = Graph()

ins = "omeka_o"

outputPath = "data/" + ins + ".rdf"

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

g.serialize(destination=outputPath)
