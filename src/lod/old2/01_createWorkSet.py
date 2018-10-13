import csv
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

f = open('data/典拠コントロール - シート1.csv', 'r')

g = Graph()

reader = csv.reader(f)
header = next(reader)
for row in reader:
    print(row)
    hojo = row[0]
    vol = row[1]
    series_id = row[2]
    work_name = row[3]
    author = row[4]

    # 異版作品

    dif_work_uri = URIRef("http://ja.dbpedia.org/resource/"+hojo+"#"+work_name)
    g.add((dif_work_uri, RDF.type, URIRef("http://example.org/class/DifferentEditionWork")))

    # 作品

    work_uri = URIRef("http://ja.dbpedia.org/resource/"+work_name)
    g.add((work_uri, RDF.type, URIRef("http://example.org/class/Work")))
    g.add((work_uri, RDFS.label,  Literal(work_name)))

    g.add((dif_work_uri, URIRef("http://example.org/property/work"), work_uri))

    # 著者

    author_uri = URIRef("http://ja.dbpedia.org/resource/" + author)
    g.add((author_uri, RDF.type, URIRef("http://example.org/class/Author")))
    g.add((author_uri, RDFS.label, Literal(author)))

    g.add((dif_work_uri, URIRef("http://example.org/property/author"), author_uri))

    # 法帖 + Vol
    '''
    hojo_v_uri = URIRef("http://ja.dbpedia.org/resource/" + hojo+"-"+vol.zfill(2))
    g.add((hojo_v_uri, RDF.type, URIRef("http://example.org/class/Hojo-V")))
    g.add((hojo_v_uri, RDFS.label, Literal(hojo+" "+vol+"巻")))
    g.add((hojo_v_uri, URIRef("http://purl.org/ontology/bibo/volume"), Literal(vol, datatype=XSD.integer)))

    g.add((dif_work_uri, URIRef("http://example.org/property/hojo-v"), hojo_v_uri))
    '''
    # 法帖

    hojo_uri = URIRef("http://ja.dbpedia.org/resource/" + hojo)
    g.add((hojo_uri, RDF.type, URIRef("http://example.org/class/Edition")))
    g.add((hojo_uri, RDFS.label, Literal(hojo)))

    # g.add((hojo_v_uri, URIRef("http://example.org/property/hojo"), hojo_uri))

    g.add((dif_work_uri, URIRef("http://example.org/property/edition"), hojo_uri))
    g.add((dif_work_uri, URIRef("http://purl.org/ontology/bibo/volume"), Literal(vol)))

g.serialize(destination='data/works.rdf')

f.close()