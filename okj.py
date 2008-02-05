#!/usr/bin/python
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

from rdflib import URIRef, Literal, RDF, RDFS
from scrape import parseDepartureArrivalInfo, arriveDepartUrl
from webfetch import fetch
from namespaces import STATION, TRAIN, TT, XS, DC
from localrdf import getGraph, addStop, addTrain, writeSubgraph
from timejunk import literalFromAmtrakTime, dateFromLiteral, literalToday
from view import trainsToday



def needsReload(graph, train, station, searchDate):
    """would we expect that the data on this train is updating, such
    that the source page needs to be refetched?

    please load into graph any contexts that might contain info about
    this train's schedule at the given station.

    previous version said:
        untilScheduled = (actual or scheduled) - datetime.datetime.now()
        if datetime.timedelta(minutes=-32) < untilScheduled < datetime.timedelta(hours=1):
            reload
    """
    return True

def addTrainInfo(graph, train, searchDate, station):
    """look up this train and write statements to a new subgraph.
    Returns url of the subgraph I wrote to

    searchDate is Literal
    """
    url = arriveDepartUrl(
        train, date=dateFromLiteral(searchDate),
        destination=graph.value(station, TT['stationCode']))

    ctxURI = URIRef(url + "#context")
    webGraph = graph.get_context(ctxURI)
    webGraph.add((ctxURI, TT['contextDate'], searchDate))

    oldGraph = graph # needs old ctx data
    
    page, pageTime = fetch(url, useCache=not needsReload(graph, train,
                                                         station, searchDate))
    webGraph.add((ctxURI, TT['fetchTime'], pageTime))
    try:
        (trainNum, parsedStation, scheduledArr, scheduledDep, actualArr,
         actualDep, status) = parseDepartureArrivalInfo(page)
    except ValueError, e:
        log.warn(e)
        webGraph.add((ctxURI, RDFS.label,
                      Literal("no info for train %s at %s on %s" %
                              (train,
                               graph.label(station),
                               searchDate))))
        
        return ctxURI

    train = addTrain(webGraph, trainNum)
    stop = addStop(graph, webGraph, train, searchDate, station)

    webGraph.add((stop, TT['station'], station))
    webGraph.add((stop, TT['date'], searchDate))

    for pred, cell in [(TT['scheduledArrivalTime'], scheduledArr),
                       (TT['scheduledDepartureTime'], scheduledDep),
                       (TT['actualArrivalTime'], actualArr),
                       (TT['actualDepartureTime'], actualDep)]:
        if cell:
            webGraph.add((stop, pred,
                          literalFromAmtrakTime(searchDate, cell)))

    if status and not (status.startswith("The scheduled ") and
                       status.endswith("Presently, no further information is available. Please check back later for updated information.")):
        webGraph.add((stop, TT['status'], Literal(status)))


    webGraph.add((ctxURI, RDFS.label,
                  Literal("times for train %s at %s on %s" %
                          (graph.label(train),
                           graph.label(station),
                           searchDate))))

    return ctxURI


def addTrainsAtStation(graph, station, searchDate):
    for train in graph.objects(station, TT['normalTrain']):
        #if '11' not in train:
        #    continue
        sub = addTrainInfo(graph, train, searchDate, station)
        writeSubgraph(graph.get_context(sub))


if __name__ == '__main__':
    graph = getGraph()
    searchDate = literalToday()

    if 1:
        addTrainsAtStation(graph, STATION['OKJ'], searchDate)
        f = open("/tmp/gr.nt", "w")
        graph.serialize(f, format="nt")
    else:
        graph.parse(open("/tmp/gr.nt"), format="nt")

    #print addTrainInfo(graph, TRAIN['n547'], searchDate, STATION['OKJ'])

    #print graph.serialize(format="n3")

    #print trainsToday(graph, searchDate, STATION['OKJ'])
