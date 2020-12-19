#!/home/ahutko/anaconda3/bin/python

import psycopg2
import datetime
from datetime import timedelta

#--------- get auto picks of deleted subnet triggers from PNSN database 
# https://internal.pnsn.org/LOCAL/WikiDocs/index.php/Accessing_the_AQMS_databases

'''
select * from trig_channel t, assocnte te, origin o where o.rflag='C' and o.algorithm='SUBTRIG' and o.evid=te.evid and t.ntid=te.ntid and t.datetime > 1597772016 and t.trigflag='t' ;
  trigid  |  ntid   | auth | subsource | sta  | net | channel | channelsrc | seedchan | location | trigflag |  datetime  | savestart  |  saveend   | rflag |           lddate           |  ntid   |   evid
 | auth | subsource | rflag |           lddate           | wfflag |  orid   |   evid   | prefmag | prefmec | commid | bogusflag |  datetime  | lat | lon | depth | mdepth | type | algorithm | algo_assoc |
auth | subsource | datumhor | datumver | gap | distance | wrms | stime | erhor | sdep | erlat | erlon | totalarr | totalamp | ndef | nbs | nbfm | locevid | quality | fdepth | fepi | ftime | vmodelid | cmo
delid | crust_type | crust_model | gtype |           lddate           | rflag
----------+---------+------+-----------+------+-----+---------+------------+----------+----------+----------+------------+------------+------------+-------+----------------------------+---------+---------
-+------+-----------+-------+----------------------------+--------+---------+----------+---------+---------+--------+-----------+------------+-----+-----+-------+--------+------+-----------+------------+-
-----+-----------+----------+----------+-----+----------+------+-------+-------+------+-------+-------+----------+----------+------+-----+------+---------+---------+--------+------+-------+----------+----
------+------------+-------------+-------+----------------------------+-------
 54647316 | 1594376 | UW   | RT1       | WAT  | UW  | EHZ     | SEED       | EHZ      |          | t        | 1597772021 | 1597772001 | 1597772065 | A     | 2020-08-18 17:36:58.986589 | 1594376 | 61671386
 | UW   | RT1       | A     | 2020-08-18 17:36:59.330563 |      1 | 1611896 | 61671386 |         |         |        |         1 | 1597772021 |   0 |   0 |     0 |        |      | SUBTRIG   |            |
UW   | RT1       |          |          |     |          |      |       |       |      |       |       |          |          |      |     |      |         |         |        |      |       |          |
      |            |             |       | 2020-08-18 17:36:59.330563 | C
'''

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
    t = datetime.datetime.utcfromtimestamp(unixtime) - timedelta(seconds=seconds_to_sub)
    return t

#----- Connect to database

dbname = os.environ['AQMS_DB']
dbuser = os.environ['AQMS_USER']
hostname = os.environ['AQMS_HOST1']  # check which is currently secondary 
dbpass = os.environ['AQMS_PASSWD']

conn = psycopg2.connect(dbname=dbname, user=dbuser, host=hostname, password=dbpass)
cursor = conn.cursor()

seismic_channels = [ 'EH', 'EN', 'HN', 'BH', 'HH' ]

#----- From database get preferred origin ids
#661505489
#cursor.execute("select * from trig_channel t, assocnte te, origin o where o.rflag='C' and o.algorithm='SUBTRIG' and o.evid=te.evid and t.ntid=te.ntid and t.datetime > 1597772016 and t.trigflag='t';")
cursor.execute("select * from trig_channel t, assocnte te, origin o where o.rflag='C' and o.algorithm='SUBTRIG' and o.evid=te.evid and t.ntid=te.ntid and t.trigflag='t';")
ncount = 0
nbad = 0
for record in cursor:
    try:
        sta = record[4]
        net = record[5]
        channel = record[6]
        chan2 = channel[0:2]
        if ( chan2 in seismic_channels ):
            channelsrc = record[7]
            seedchan = record[8]
            location = record[9]
            if ( location == '  ' or location == '' ):
                loc = '--'
            else:
                loc = location
            trigflag = record[10]
            date_time = record[11]
            savestart = record[12]
            saveend = record[13]
            rflag = record[14]
            strdate = unix_to_true_time(int(record[11])).strftime("%Y-%m-%dT%H:%M:%S.%f")
            ncount = ncount + 1
            nslc = net + '.' + sta + '.' + loc + '.' +  channel
            print( nslc, strdate, 'ds zz A' )
    except:
            print('BAD: ',record)
            nbad = nbad + 1


