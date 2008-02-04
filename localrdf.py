import os, md5
from rdflib.Graph import ConjunctiveGraph, Graph
from rdflib import BNode, URIRef, Literal
from rdflib import RDF, RDFS
from namespaces import TT, TRAIN, DC

def get_context(self, identifier, quoted=False):
    assert isinstance(identifier, URIRef) or \
           isinstance(identifier, BNode), type(identifier)
    return Graph(store=self.store, identifier=identifier,
                 namespace_manager=self)
ConjunctiveGraph.get_context = get_context

def getGraph():
    """
    get the main graph, including data from trains.n3 on disk
    """
    graph = ConjunctiveGraph()
    graph.parse("trains.n3", format="n3", publicID=TT['disk#context'])
    return graph

def addStop(readGraph, writeGraph, train, date, station):
    """URI for a train stop. date is xs:date"""
    stop = URIRef("%s/%s/%s" % (train, date,
                                readGraph.value(station, TT['stationCode'])))
    writeGraph.add((stop, RDF.type, TT['Stop']))
    writeGraph.add((train, TT['stop'], stop))
    return stop

def addTrain(graph, trainNum):
    train = TRAIN["n" + trainNum]
    graph.add((train, RDF.type, TT['Train']))
    graph.add((train, RDFS.label, Literal(str(trainNum))))
    return train

SUBGRAPH_FORMAT = "xml"

def filenameFromURI(uri):
    return md5.md5(uri).hexdigest()

def writeSubgraph(subgraph):
    created = subgraph.value(subgraph.identifier, TT['contextDate'])
    assert created
    filename = "graph/%s/%s" % (created, filenameFromURI(subgraph.identifier))
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    subgraph.serialize(open(filename, "w"), format=SUBGRAPH_FORMAT)
    open(filename + ".uri", "w").write(str(subgraph.identifier) + "\0" +
                                       str(subgraph.label(subgraph.identifier)))
    
def subgraphs(date):
    """generator of (uri, ntfilename)

    pass a date literal like '2008-02-03' to get all the data for that date
    """
    dateDir = "graph/%s" % date
    if not os.path.isdir(dateDir):
        return
    for name in os.listdir(dateDir):
        filename = "graph/%s/%s" % (date, name)
        if filename.endswith('.uri'):
            continue
        uri, label = open(filename + ".uri").read().split("\0")
        yield uri, label, filename
        
def readSubgraphXML(filename):
    if SUBGRAPH_FORMAT == 'xml':
        return open(filename).read()
    g = ConjunctiveGraph()
    g.parse(filename, format=SUBGRAPH_FORMAT)
    return g

def allGraphs(date):
    """a graph with all the data we have for a given date, like '2008-02-03'"""
    g = getGraph()
    for uri, label, filename in subgraphs(date):
        if not label:
            label = "(no label provided)"
        g.parse(filename, format=SUBGRAPH_FORMAT)
    return g
