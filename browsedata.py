#!/usr/bin/python
import logging, sys, inspect

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

#sys.path.append("rdflib/rdf/build/lib")
#from rdf.plugins import register
#register('rdf.IOMemory', 

#sys.path.insert(0, "rdflib-2.4.x/build/lib.linux-i686-2.5")

from rdflib.Graph import Graph
from rdflib import URIRef, Literal, StringInputSource
from rdflib import RDF, RDFS
print inspect.getabsfile(Literal)

from namespaces import STATION, TRAIN, TT, XS, INITNS
from localrdf import getGraph, subgraphs, readSubgraphXML, allGraphs
from timejunk import literalToday
from twisted.internet import reactor
from twisted.python import log as tlog
from twisted.web import http
from nevow.appserver import NevowSite
from nevow import rend, loaders, tags as T, inevow

from okj import addTrainsAtStation

from serverdf import RdfXMLPage



class Main(rend.Page):
    docFactory = loaders.xmlfile("templates/main.html")

    def child_graph(self, ctx):
        return GraphPage()
    
    def child_okj(self, ctx):
        graph = allGraphs(literalToday())
        child = viewFunc('trainsToday', graph, literalToday(), STATION['OKJ'])
        def update(self, ctx):
            request = inevow.IRequest(ctx)
            graph = Graph()
            graph.parse("passwd.n3", format="n3")
            g = lambda pred: graph.value(TT['okjUpdate'], pred)
            if ((request.getUser(), request.getPassword()) ==
                (g(TT['user']), g(TT['password']))):
                graph = getGraph()
                addTrainsAtStation(graph, STATION['OKJ'], literalToday())
                return "update ok"
            else:
                request.setHeader('WWW-Authenticate',
                                  'Basic realm="traintimes"')
                request.setResponseCode(http.UNAUTHORIZED)
            return "Authentication required." 

        child.child_update = lambda ctx: update(child, ctx)
        return child

    def child_bos(self, ctx):
        graph = allGraphs(literalToday())
        return viewFunc('next4Trains', graph, STATION['BOS'])

    def child_pvd(self, ctx):
        graph = allGraphs(literalToday())
        return viewFunc('next4Trains', graph, STATION['PVD'])

def viewFunc(name, *args):
    import view
    reload(view)
    class P(rend.Page):
        def renderHTTP(self, ctx):
            return getattr(view, name)(*args)
    return P()
            

class GraphPage(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile("templates/graph.html")
    
    def render_graphs(self, ctx, data):
        for uri, label, filename in sorted(subgraphs(literalToday()),
                                           key=lambda (u,l,f): l):
            filename = filename[len("graph/"):]
            yield T.li[T.a(href=filename)[label], " ",
                       T.a(href=[filename, "?type=n3"])[T.code["[N3/text]"]]]
               

    def locateChild(self, ctx, segments):
        if segments == ('all',):
            g = allGraphs(literalToday())
            return RdfXMLPage(g.serialize(format='xml')), []

        print segments
        # limiting to today's data only because it was easier to code quickly
        if len(segments) == 2 and segments[0] == str(literalToday()) and segments[1].isalnum():
            return RdfXMLPage(readSubgraphXML("graph/%s/%s" % segments[:2])), []
        return rend.Page.locateChild(self, ctx, segments)


tlog.startLogging(sys.stdout)
reactor.listenTCP(8008, NevowSite(Main()))
reactor.run()
