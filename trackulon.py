#!/usr/bin/env python2.7

debug = True

import csv
import sqlite3
import urllib
import xml.etree.ElementTree as ET

# my modulelet with basic data
from trackulonData import *

def buildRequests(trainStations):
    '''
    Constructs all the API requests that will be used by this program.
    '''
    stations = trainStations.keys()

    reqURLs = []
    # get groups of MAXREQ mapids
    for ii in range(0, len(stations)/MAXREQ):
        idx = ii*MAXREQ
        reqURLs.append(baseURL + "".join(["&mapid=" + str(x) for x in stations[idx:idx+MAXREQ]]))

    # get remaining mapids
    idx = MAXREQ*(len(stations)/MAXREQ)
    reqURLs.append(baseURL + "".join(["&mapid=" + str(x) for x in stations[idx:]]))

    return reqURLs

reqURLs = buildRequests(trainStations)

opener = urllib.FancyURLopener()

conn = sqlite3.connect('trackulon.db')
c = conn.cursor()

c.execute('''create table if not exists etas (tmst text, staId integer,
               stpId integer, staNm text, stpDe text, rn integer, rt text,
               destSt integer, destNm text, trDr integer, prdt text, arrT text,
               isApp integer, isSch integer, isFlt integer, isDly integer,
               flags blob, lat real, lon real, heading integer)''')

tags = ['tmst', 'staId', 'stpId', 'staNm', 'stpDe', 'rn', 'rt', 'destSt',
'destNm', 'trDr', 'prdt', 'arrT', 'isApp', 'isSch', 'isFlt', 'isDly', 'flags',
'lat', 'lon', 'heading']

# TODO: work in tmst

sqlStr = 'insert into etas values (?' + ',?'*(len(tags) - 1) + ')'

etas = [] # list of eta tuples

for reqURL in reqURLs:
    if debug:
        print(reqURL)

    r = opener.open(reqURL)

    e = ET.parse(r)
    root = e.getroot()
    for eta in root.iter('eta'):
        values = [""] # first value is placeholder for tmst
        for elem in eta.iter():
            if (elem.tag != 'eta'):
                if debug:
                    print(elem.tag, elem.text)
                values.append(elem.text)
        etas.append(tuple(values))


c.executemany(sqlStr, etas)
        # if eta.find('isSch').text != "1":
        #     print ",".join([eta.find('rt').text,
        #                    eta.find('rn').text,
        #                    eta.find('prdt').text,
        #                    eta.find('arrT').text])

conn.commit()
conn.close()