import logging, os
from namespaces import STATION, TRAIN, TT, XS, INITNS
from timejunk import literalNow
from genshi.template import TemplateLoader
from genshi.builder import tag as T

loader = TemplateLoader(
    [os.path.join(os.path.dirname(__file__), 'templates')],
    auto_reload=True)

def trainsToday(graph, searchDate, station):
    """rendered template text"""
    #print repr(searchDate)
    #print "subjs", len(list(graph.subjects(None, searchDate)))
    #print "dates", len(list(graph.triples((None, TT['date'], None))))
    # this was returning no rows in rdflib-2.4.x branch!
    #print list(graph.query('''SELECT ?d WHERE { ?x tt:date ?d }''', initNs=INITNS))

    dataRows = []
    for (searchDate2, trainNumber, trainName, tsa, taa, tsd, tad, status
         ) in graph.query(
        """SELECT ?searchDate ?trainNumber ?trainName
                  ?tsa ?taa ?tsd ?tad ?status WHERE {
             ?train a tt:Train;
                    rdfs:label ?trainNumber;
                    tt:stop ?stop .
             ?stop tt:date ?searchDate;
                   tt:station ?station .
             OPTIONAL { ?train tt:trainName ?trainName . }
             OPTIONAL { ?stop tt:status ?status . }
             OPTIONAL { ?stop tt:scheduledDepartureTime ?tsd . }
             OPTIONAL { ?stop tt:actualDepartureTime ?tad . }
             OPTIONAL { ?stop tt:scheduledArrivalTime ?tsa . }
             OPTIONAL { ?stop tt:actualArrivalTime ?taa . }
            }""", initNs=INITNS,
        initBindings={#'?searchDate' : searchDate,
                      '?station' : station}):
        if repr(searchDate2) != repr(searchDate): # workaround for sparql err
            continue
        dataRows.append((tad, taa, tsd, tsa, trainNumber, trainName, status))
    dataRows.sort(key=lambda r: [t for t in r[:4] if t]) # fancier ORDER BY

    rows = []
    now = literalNow()
    shownNow = False
    nowRow = T.tr(T.td("now", colspan="4", align="center", bgcolor="#D88585"))
    for (tad, taa, tsd, tsa, trainNumber, trainName, status) in dataRows:

        scheduledTime = tsd or tsa
        actualTime = tad or taa  # or 'estimated'
        
        if (actualTime or scheduledTime) > now and not shownNow:
            rows.append(nowRow)
            shownNow = True
            
        rows.append(T.tr(T.td(trainNumber, " ", trainName,
                              class_="trainNumber"),
                         T.td(scheduledTime),
                         T.td(actualTime, bgcolor="#EDEAD0"),
                         T.td(status)))
    if not shownNow:
        rows.append(nowRow)

    rows = T(*rows)
    tmpl = loader.load("okjtimes.html")
    return tmpl.generate(rows=rows, lastScan='?',
                         today=searchDate).render('html')
        


def next4Trains(graph, station):
    stationLabel = graph.label(station)
    rows = []
    for (trainLabel, departTime) in graph.query(
        """SELECT ?trainLabel ?dep WHERE {
               ?train a tt:Train;
                      rdfs:label ?trainLabel;
                      tt:stop [
                          tt:station ?station;
                          tt:scheduledDepartureTime ?dep
                          ] .
           } ORDER BY ?dep""", initNs=INITNS,
        initBindings={'?station' : station}):
        print "train %s leaves %s at %s" % (trainLabel, stationLabel, departTime)
        rows.append((trainLabel, departTime))

    tmpl = loader.load("next4.html")
    return tmpl.generate(rows=rows, start=graph.label(station)).render('html')
        
