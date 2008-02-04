from rdflib import Namespace, RDFS

STATION = Namespace("http://traintimes.bigasterisk.com/station/")
TRAIN = Namespace("http://traintimes.bigasterisk.com/carrier/amtrak/train/")
TT = Namespace("http://traintimes.bigasterisk.com/v1#")
XS = Namespace("http://www.w3.org/2001/XMLSchema#")
INITNS = dict(tt=TT, station=STATION, rdfs=RDFS.RDFSNS)
DC = Namespace("http://purl.org/dc/terms/")
