
import logging, optparse, urllib, time, datetime, pprint, pickle, os, cgitb, re
import TableParse
from BeautifulSoup import BeautifulSoup
import BeautifulSoup as bsoupmod
from timejunk import todayDateTime
from rdflib import URIRef
log = logging.getLogger()

# something in the code needs greater than version 2
log.info("BeautifulSoup version %s", bsoupmod.__version__)

def fetchTrainInfo(trainNumber):
    return fetchTrainInfo2(trainNumber, destination="OKJ")

def fetchTrainInfo2(trainNumber, destination='', origin=''):
    """
    provide one of origin or destination, which are like "OKJ"

    returns
    scheduled datetime, actual datetime, isEstimate, note"""
    today = datetime.date.today()
    t1 = time.time()
    result = urllib.urlopen(arriveDepartUrl(trainNumber, destination, origin)).read()

    log.debug("read train %s in %.3f seconds" % (trainNumber, time.time() - t1))

    return parse(result)


def trainNumberFromURI(train):
    # don't have all the train numbers in the graph yet. figure them
    # out in getGraph!
    return train.rsplit('n', 1)[-1]

def arriveDepartUrl(trainNumber='', date='<today>', destination='', origin=''):

    if isinstance(trainNumber, URIRef):
        trainNumber = trainNumberFromURI(trainNumber)
    
    if date == '<today>':
        date = datetime.date.today()
    log.debug("arriveDepartUrl on date %r" % date)

    xwdf_destination = 'departLocation'
    if origin:
        xwdf_destination = 'arriveLocation'

    assert bool(origin) or bool(destination), "need to set origin or destination"

    return "&".join(("""\
http://tickets.amtrak.com/itd/amtrak?requestor=amtrak.presentation.handler.page.rail.AmtrakRailGetTrainStatusPageHandler
xwdf_origin=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FdepartLocation%2Fsearch
wdf_origin="""+origin+"""
xwdf_trainNumber=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FsegmentRequirements%5B1%5D%2FserviceCode
wdf_trainNumber="""+trainNumber+"""
xwdf_destination=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2F"""+xwdf_destination+"""%2Fsearch
wdf_destination="""+destination+"""
%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.monthyear="""+("%04d-%02d" % (date.year, date.month))+"""
%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.day="""+("%02d" % date.day)+"""
%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartTime.hourmin=
xwdf_SortBy=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate%2F%40radioSelect
wdf_SortBy=arrivalTime
xwdf_SortBy=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate%2F%40radioSelect
_handler%3Damtrak.presentation.handler.request.rail.AmtrakRailTrainStatusSearchRequestHandler%2F_xpath%3DsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D.x=59
_handler%3Damtrak.presentation.handler.request.rail.AmtrakRailTrainStatusSearchRequestHandler%2F_xpath%3DsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D.y=21""").splitlines())

def checkAmtrakError(page):
    """raise if there's an error on the page, except for bogus error
    500S which doesn't actually stop results from showing"""
    # <br>[ forces the error in the page, not the ones in the <script> area
    if '<br>[Error ID' in page and '<br>[Error ID: 500S' not in page:
        i = page.index('<br>[Error ID')
        raise ValueError("error on amtrak page: ...%s..." % page[i-200: i+20])

def parseTrainStatusChoice(result):
    """
    page with a few trains to choose from
    """
    checkAmtrakError(result)
    soup = BeautifulSoup(result)
    selecttrain = soup.find('table', attrs={'class' : 'selecttrain'})
    ret = []
    for tr in selecttrain.findAll('tr'):
        tds = tr.findAll('td')
        if 'type="radio"' not in str(tds[0]):
            continue

        trainNum = tds[1].contents[0].strip().split()[0]
        dep = tds[2].contents
        arr = tds[3].contents
        depStation = dep[3].contents[0]  # "PVD"
        depTime = dep[7].string # "8:19 pm"
        arrStation = arr[5].contents[0] # "BOS"
        arrTime = arr[9].string # "11:15 pm"
        ret.append((trainNum, depTime, depStation, arrTime, arrStation))
    return ret

def parseDepartureArrivalInfo(result):
    """
    page with a single train+station time info.
    """
    checkAmtrakError(result)
    soup = BeautifulSoup(result.replace("</td>\r\n</td>", "</td>")) # amtrak, you CRAZY
    selecttrain = soup.find('table', attrs={'class' : 'selecttrain'})

    tr = selecttrain.findAll('tr')[-1]
    tds = tr.findAll('td')

    trainNum = tds[0].string.strip().split()[0]
    station = tds[1].contents[-4].contents[0]

    scheduledArr = parseTimeCell(tds[2])
    scheduledDep = parseTimeCell(tds[3])
    actualArr = parseTimeCell(tds[4])
    actualDep = parseTimeCell(tds[5])

    status = ''.join(map(str, tds[6].contents)).strip().replace("<br />", "")

    return trainNum, station, scheduledArr, scheduledDep, actualArr, actualDep, status

def parseTimeCell(elem):
    """
    contents might be like one of these:
     [u'&nbsp;']
     [u'\n', <b>(6:38 pm)</b>, u'\n', <br />, <i>estimated</i>, u'\n']
     [u'\n', <b>4:25 pm</b>, u'\n', <br />, u'02-FEB-08\r\n\r\n']
     [u'\n', <b>7:25 pm</b>, u'\n']
     [u'\n']
     
    return is the time like '7:25 pm' or ''
    """
    s = str(elem).replace("\n", "").replace("\r", "")
    m = re.search(r'(\d+:\d+ [ap]m)', s)
    if m:
        return m.group(1)
    return ''

def parseOriginalStyle():
    cells = TableParse.parse(result)
    log.debug(pprint.pformat(list(enumerate(cells))))
    tableNum = 35

    scheduled = todayDateTime((cells[tableNum][2] or cells[tableNum][3]).splitlines()[0])

    actualCell = (cells[tableNum][4] or cells[tableNum][5])
    if actualCell:
        actual = todayDateTime(actualCell.splitlines()[0].replace('(','').replace(')',''))
        isEstimate = 'estimated' in actualCell
    else:
        actual = None
        isEstimate = False

    note = cells[tableNum][6]
    return scheduled, actual, isEstimate, note

def trainArriveDepart(train, station, date):
    """
    add URLs to the graph for 
    """

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    multi = open("/tmp/trains").read()
    print parseTrainStatusChoice(multi)

    print parseDepartureArrivalInfo(open("/tmp/train2").read())

    #url = arriveDepartUrl('733', destination='OKJ')
    #print parseDepartureArrivalInfo(urllib.urlopen(url).read())
    

    raise SystemExit()
    print '''<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>    <title></title>  </head>  <body>

<ol>
<li><a href="http://tickets.amtrak.com/itd/amtrak?requestor=amtrak.presentation.handler.page.rail.AmtrakRailTrainStatusSelectTrainPageHandler&xwdf_origin=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FdepartLocation%2Fsearch&wdf_origin=Providence%2C+RI+%28PVD%29&xwdf_trainNumber=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FsegmentRequirements%5B1%5D%2FserviceCode&wdf_trainNumber=&xwdf_destination=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtravelSelection%2FjourneySelection%5B1%5D%2FarriveLocation%2Fsearch&wdf_destination=Boston+-+South+Station%2C+MA+%28BOS%29&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.monthyear=2008-01&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate.day=27&%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartTime.hourmin=&xwdf_SortBy=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate%2F%40radioSelect&wdf_SortBy=arrivalTime&xwdf_SortBy=sessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2FtripRequirements%2FjourneyRequirements%5B1%5D%2FdepartDate%2F%40radioSelect&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&wdf_jn1=tk8tkwbnncdl&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&xwdf_jn1=%2FsessionWorkflow%2FproductWorkflow%5B%40product%3D%27Rail%27%5D%2Fjourney%5B1%5D%2F%40id&_handler%3Dcom.sita.ats.amtrak.presentation.handler.request.rail.AmtrakRailScheduleLedGetJourneyStatusRequestHandler.x=71&_handler%3Dcom.sita.ats.amtrak.presentation.handler.request.rail.AmtrakRailScheduleLedGetJourneyStatusRequestHandler.y=7">destination BOS</a></li>
'''
    
    monday = datetime.date(2008,1,28)

    for line in ('''\
arriveDepartUrl('733', destination='OKJ')
arriveDepartUrl("733", destination="BKY")
arriveDepartUrl("733", origin="BKY", destination="OKJ")
arriveDepartUrl(origin="PVD", destination="BOS")
arriveDepartUrl("194", destination="BOS")
arriveDepartUrl(date=monday, origin="PVD", destination="BOS")
'''.splitlines()):
        print '<li><a href="%s">%s</a></li>' % (eval(line), line)

    print '''  </body></html>    '''

