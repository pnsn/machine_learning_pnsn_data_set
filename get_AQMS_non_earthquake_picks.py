#!/home/ahutko/anaconda3/bin/python

import os
import psycopg2
from datetime import datetime, timedelta

#--------- get picks from PNSN database for various source types
# https://internal.pnsn.org/LOCAL/WikiDocs/index.php/Accessing_the_AQMS_databases

#arrival table:
#rflag: H = human, A = automatic, F = finalized
#archdb=> select * from arrival limit 10;
#   arid   | commid |     datetime     | sta  | net | auth | subsource | channel | channelsrc | seedchan | location | iphase | qual | clockqual | clockcorr | ccset | fm | ema | azimuth | slow | deltim | d
#elinc | delaz | delslo | quality | snr | rflag |       lddate        
#----------+--------+------------------+------+-----+------+-----------+---------+------------+----------+----------+--------+------+-----------+-----------+-------+----+-----+---------+------+--------+--
#------+-------+--------+---------+-----+-------+---------------------
# 10576803 |        | 1329276740.71738 | KEB  | NC  | UW   | Jiggle    |         |            | HHZ      |          | P      | i    |           |           |       | d. |     |         |      |   0.06 |      |       |        |     0.8 |     | H     | 2012-03-12 18:33:05
# 10576808 |        |  1329276770.3577 | KEB  | NC  | UW   | Jiggle    |         |            | HHN      |          | S      | e    |           |           |       | .. |     |         |      |    0.3 |      |       |        |     0.3 |     | H     | 2012-03-12 18:33:05
# 10576813 |        | 1329276742.40491 | TAKO | UW  | UW   | Jiggle    |         |            | BHZ      |          | P      | i    |           |           |       | c. |     |         |      |   0.06 |      |       |        |     0.8 |     | H     | 2012-03-12 18:33:05
# 10576818 |        | 1329276774.06588 | TAKO | UW  | UW   | Jiggle    |         |            | BHE      |          | S      | e    |           |           |       | .. |     |         |      |   0.15 |       |       |        |     0.5 |     | H     | 2012-03-12 18:33:05

#----- Convert unix/epoc time to truetime which includes leap seconds.
#      Input is a timestamp, e.g. 1568130188.11
#      Output is a datetime object, e.g. datetime.datetime(2019, 9, 10, 15, 42, 41, 117380)
def unix_to_true_time(unixtime):
    leap_seconds = {2272060800: 10 ,2287785600: 11 ,2303683200: 12 ,2335219200: 13 ,2366755200: 14 ,2398291200: 15 ,2429913600: 16 ,2461449600: 17 ,2492985600: 18 ,2524521600: 19 ,2571782400: 20 ,2603318400: 21 ,2634854400: 22 ,2698012800: 23 ,2776982400: 24 ,2840140800: 25 ,2871676800: 26 ,2918937600: 27 ,2950473600: 28 ,2982009600: 29 ,3029443200: 30 ,3076704000: 31 ,3124137600: 32, 3345062400: 33 ,3439756800: 34 ,3550089600: 35 ,3644697600: 36 ,3692217600: 37}
    time1900 = unixtime + 2208988800
    seconds_to_sub = 0
    for utime in leap_seconds:
        if ( time1900 >= utime ):
            seconds_to_sub = leap_seconds[utime] - 10
    t = datetime.utcfromtimestamp(unixtime) - timedelta(seconds=seconds_to_sub)
    return t

#----- Connect to database

dbname = os.environ['AQMS_DB']
dbuser = os.environ['AQMS_USER']
hostname = os.environ['AQMS_HOST1']  # check which is currently secondary 
dbpass = os.environ['AQMS_PASSWD']

conn = psycopg2.connect(dbname=dbname, user=dbuser, host=hostname, password=dbpass)
cursor = conn.cursor()

NLimit = 10000    #-- max number of events to consider per source type
seismic_channels = [ 'EN', 'HN', 'BH', 'HH' ]

#----- Loop over various types of events.
#sources = [ 'eq', 'su', 'th', 'px', 'ex', 'sn', 'ls', 'pc', 'mi', 've' ] 
sources = [ 'su', 'th', 'px', 'ex', 'sn', 'ls', 'pc', 'mi', 've' ]
#sources = [ 'px' ]
arrivals = {}
for source in sources:

    #----- From database get preferred origin ids
    cursor.execute('select * from event where etype = (%s) and lddate > (%s) order by evid desc limit (%s);', (source,'1969-01-01',NLimit ) )
    prefor = {}
    for record in cursor:
        orid = record[1]
        prefor[orid] = []

    #----- In table assocaro, go through each origin id and get the arrival ids
    for orid in prefor:
        cursor.execute('select * from assocaro where orid = (%s);', (orid,) )
        for record in cursor:
            arrid = record[1]
            prefor[orid].append(arrid)

    #----- Now use table arrival and get sncls, dates, labels (P,S) and 
    #      qualities (i=impulsive,e=emergent) for each arrival and
    #      rflag, F = finalized, H = hand (saved but not necessarily finalized)
    arrivals[source] = {}
    for orid in prefor:
        for arid in prefor[orid]:
#            cursor.execute('select * from arrival where arid = (%s) and seedchan != (%s) and seedchan != (%s);', (arid,'EH?','SH?') )
            cursor.execute('select * from arrival where arid = (%s) ;', (arid,) )
            try:
                for record in cursor:
                    date = int(record[2])
                    sta = record[3]
                    net = record[4]
                    chan = record[9]
                    if ( chan[0:2] not in seismic_channels ): continue
                    loc = record[10]
                    if ( loc == "  " or loc == "" ): loc = "--"
                    iflag = 0
                    phase = record[11]
                    qual = 'z'
                    if ( record[12] != None ):
                        qual = record[12]
                    else:
                        try:
                            #-- from old UW2AQMS system, use deltime for quality
                            #    https://internal.pnsn.org/LOCAL/WikiDocs/index.php/UW2_to_AQMS
                            fqual = abs(float(record[20]))
                            if ( fqual <= 0.06 ):
                                qual = 'i'
                            elif ( qual > 0.06 ):
                                qual = 'e'
                            else:
                                qual = 'n'
                            iflag = 1
                        except:
                            iflag = 2
                            qual = 'z' + record[20]
                    phasequal = phase + qual
                    rflag = record[26]
                    arrivals[source][arid] = [source, date, sta, net, loc, chan, phasequal, rflag ]
                    strdate = unix_to_true_time(date).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    output = net + "." + sta + "." + loc + "." + chan + " " + strdate + ' ' + source + ' ' + phasequal + " " + rflag
                    print(output)
            except:
                ijunk = 1

print("COUNTS: ")
print("SU: ",len(arrivals['su']), "TH: ",len(arrivals['th']), "PX: ",len(arrivals['px']), "EX: ",len(arrivals['ex']), "SN: ",len(arrivals['sn']), "LS: ", len(arrivals['ls']), "PC: ", len(arrivals['pc']), "MI: ",len(arrivals['mi']), "VE: ", len(arrivals['ve']) )

