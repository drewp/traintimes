from nevow import rend, inevow
from namespaces import STATION, TRAIN
from rdflib.Graph import Graph
from rdflib import StringInputSource

class RdfXMLPage(rend.Page):
    """serve some rdf data"""
    def __init__(self, xml):
        self.xml = xml
    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        if ctx.arg('type') == 'n3':
            request.setHeader('Content-Type', 'text/plain')
            graph = Graph()
            graph.parse(StringInputSource(self.xml), format='xml')
            graph.bind('station', STATION)
            graph.bind('train', TRAIN)
            return graph.serialize(format='n3')
        else:
            request.setHeader("Content-Type", "application/rdf+xml")
            return self.xml
