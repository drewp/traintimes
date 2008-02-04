import time, datetime
from rdflib import Literal
from xml.utils import iso8601
from namespaces import XS

def literalFromAmtrakTime(date, t):
    """
    date is xs:date Literal
    t is like '8:53 pm' or '(9:53 pm)'

    i'm totally omitting the timezone for now
    """
    secs = time.mktime(time.strptime(str(date) + " " + t.strip('()'),
                                     "%Y-%m-%d %I:%M %p"))
    wrongZone = iso8601.ctime(secs)
    noZone = wrongZone.rsplit('-', 1)[0]
    return Literal(noZone, datatype=XS['dateTime'])

def literalFromDate(d):
    """omits timezone"""
    return Literal(d.isoformat(), datatype=XS['date'])

def dateFromLiteral(d):
    return datetime.date(*[int(x.lstrip('0')) for x in d.split('-')])

def literalToday():    # missing time zone, just using local one
    return literalFromDate(datetime.date.today())

def literalNow(): # missing zone
    wrongZone = iso8601.ctime(time.time())
    return Literal(wrongZone, datatype=XS['dateTime'])

# for older code
def todayDateTime(s):
    """given '4:06 pm', returns a datetime on today"""
    t = datetime.datetime(*time.strptime(s, "%I:%M %p")[0:6])
    return datetime.datetime.combine(datetime.date.today(), t.timetz())

def literalFromTime(secs='now'):
    if secs == 'now':
        secs = time.time()
    # wrong formatting for :00 seconds, i think.
    # timezone may be wrong too :(
    i = iso8601.tostring(secs, [time.timezone, time.altzone][time.daylight])
    return Literal(i, datatype=XS['dateTime'])
