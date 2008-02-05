import logging, urllib, os.path
from timejunk import literalFromTime

log = logging.getLogger()
def fetch(url, useCache=True):
    """returns page text and the time of the actual fetch"""
    local = "webcache/%s" % abs(hash(url))
    if useCache:
        try:
            ret = open(local).read()
            log.debug("using local cache of %s at %s" % (url, local))
            return ret, literalFromTime(os.path.getmtime(local))
        except IOError:
            pass
    
    log.debug("fetching %s" % url)
    data = urllib.urlopen(url).read()
    open(local, "w").write(data)
    return data, literalFromTime()
