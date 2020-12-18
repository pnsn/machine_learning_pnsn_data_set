#!/home/ahutko/anaconda3/bin/python

'''
Alex Hutko, UW, Nov 9, 2020

1) From NEIC comcat, get all events from 2018-2020.11 in 4 categories:
  a) M4.3 - M5.0 within the west coast (Lat:25to55, Lon:-135to100)
  b) M5.0+ for all North American events (Lat:20to65, Lon:-165to-75)
  c) M6.0+ globally w depth < 100km
  d) M6.0+ globally w depth > 100km

Example query using the NEIC API:
https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?format=xml&starttime=2014-01-01&endtime=2014-01-02&minmagnitude=5&format=text

output of NEIC API:
#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName
usc000lvb5|2014-01-01T16:03:29.000|-13.8633|167.249|187|us|us|us|usc000lvb5|mww|6.5|us|32km W of Sola, Vanuatu
usc000lv5e|2014-01-01T00:01:16.610|19.0868|120.2389|10.07|us|us|us|usc000lv5e|mb|5.1|us|76km NNW of Davila, Philippines

2) Get list of all broadband stations at IRIS for networks:
   AZ, CI, BK, NC, OO, US, CC, UO, UW, CN, NN, IU, II

3) For each station, randomly choose X events from each of 4 categories.
   Didn't get around to: make sure events chosen have flat(ish) histogram w distance.

4) Download a generous window of data around predicted first arrival time.

5) Use an STA/LTA to estimate where P-wave is within 5 sec of predicted time.
   Didn't get around to: apply average station dt shift from IRIS event plot MCCC

6) Apply some EPIC processing and estimate if arrival would cause a trigger.

7) Cut the ZNE data to -5 to +10 sec and write a labled output file in HDF5.

Notes: 
-P-wavelets that are in the coda of a recent event are intentionally not screened out.
-Intentional speed bumps are placed before each request.  IRIS FDSN WS will block your
  IP of all requests for 20 sec when N requests of any kind/sec > ~100.

Note to self: fix the station starttime/endtime issue so that you only try to fetch that which exists e.g. BHZ vs HHZ

'''

import os
import psutil
import datetime
from datetime import timedelta
import requests
import numpy as np
import math
from obspy.geodetics import locations2degrees
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.signal.trigger import classic_sta_lta
import obspyh5
import time
import random
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from get_data_metadata import *
import timeit

client = Client("IRIS")

#----- function to check if your IP is in the IRIS FDSNWS 20 sec penalty box
def check_IRIS_WS():
    try:
        time.sleep(0.05)
        starttime = UTCDateTime("2002-01-01")
        endtime = UTCDateTime("2002-01-02")
        inventory = client.get_stations(network="IU", station="ANMO",
                                starttime=starttime,endtime=endtime)
    except:
        nowtime = datetime.datetime.now()
        print('In IRIS IP jail ', nowtime.strftime("%Y-%m-%dT%H:%M:%S"))
        time.sleep(90)

#----- set the max number of P wavelets per station for each of 4 quake types

Nmax_per_station = 10000
Tfirst = datetime.datetime(2010,1,1,0,0,0)
Tlast = datetime.datetime(2025,1,1,0,0,0)
TbeforeP = int(60)
TafterP = int(60)
minlen = TafterP + TbeforeP - 1
sample_rate = 100
HPcorner = 0.075  # high pass filter corner
Tpadding = 3./HPcorner
sta = 0.05
lta = 5.0
ista = int(sta*sample_rate)
ilta = int(lta*sample_rate)
mpd,dt,twin = 10, 0.01, 4.0
MinSTALTA = 3    # STA/LTA threshold in a +/- 10sec window around P for keeping results

#----- Function to get good-enough precalculated travel times very quickly.
TT_table_read = False
depths = []
TTs = []
def get_TT(depth,dist):
    global TT_table_read, depths, TTs
    if ( TT_table_read is False ):
        TT_table_read = True
        fTT = open('TT.iasp91.P')
        TTlines = fTT.read().splitlines()
        fTT.close()
        depths = [ -999, 0, 10, 20, 30, 35, 40, 50, 70, 90, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700 ]
        n = 0
        for line in TTlines:
            n = n + 1
            if ( n > 1 ):
                line0 = line.split(' ')
                x = [float(i) for i in line0]
                TTs.append(x)
    iy1 = math.floor(dist)
    iy2 = math.ceil(dist)
    ix = -1
    for d in depths:
        ix = ix + 1
        if ( depth == d ):
            ix1 = ix
            ix2 = ix
        elif ( d > depth ):
            ix2 = ix
            ix1 = ix - 1
            break
    fracX = ( depth - depths[ix1] ) / ( depths[ix2] - depths[ix1] )
    fracY = dist - math.floor(dist)
    TTiy1ix1 = TTs[iy1][ix1]
    TTiy2ix1 = TTs[iy2][ix1]
    TTiy1ix2 = TTs[iy1][ix2]
    TTiy2ix2 = TTs[iy2][ix2]
    TTiyix1 = TTs[iy1][ix1] + fracY * ( TTs[iy2][ix1] - TTs[iy1][ix1] )
    TTiyix2 = TTs[iy1][ix2] + fracY * ( TTs[iy2][ix2] - TTs[iy1][ix2] )
    TT = TTiyix1 + fracX * ( TTiyix2 - TTiyix1 )
    return(TT)

#----- Fetch events from comcat

print('Fetching quakes')
latitude = 46.
longitude = -120.5
T1 = Tfirst - timedelta(minutes = 35)
T2 = Tlast + timedelta(minutes = 61)
T1str = T1.strftime("%Y-%m-%dT%H:%M:%S")
T2str = T2.strftime("%Y-%m-%dT%H:%M:%S")

url1 = ("https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=" + T1str + "&endtime=" + T2str + "&minlatitude=25.&maxlatitude=55.&minlongitude=-135.&maxlongitude=-100.&minmagnitude=4.0&maxmagnitude=5.0&format=text")
url2 = ("https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=" + T1str + "&endtime=" + T2str + "&minlatitude=20.&maxlatitude=65.&minlongitude=-165.&maxlongitude=-75.&minmagnitude=5.0&format=text")
url3 = ("https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=" + T1str + "&endtime=" + T2str + "&minmagnitude=6.0&maxdepth=100&format=text")
url4 = ("https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=" + T1str + "&endtime=" + T2str + "&minmagnitude=6.0&mindepth=100&format=text")

lines1, lines2, lines3, lines4 = [], [], [], []
f1 = requests.get(url1)
for line in f1.iter_lines():
    lines1.append(line.decode('utf-8'))
f2 = requests.get(url2)
for line in f2.iter_lines():
    lines2.append(line.decode('utf-8'))
f3 = requests.get(url3)
for line in f3.iter_lines():
    lines3.append(line.decode('utf-8'))
f4 = requests.get(url4)
for line in f4.iter_lines():
    lines4.append(line.decode('utf-8'))
lines = [ lines1, lines2, lines3, lines4 ]

# output looks like:
# 'us2000d0ex|2018-02-10T22:50:48.880|-3.8176|151.9248|268|us|us|us|us2000d0ex|mww|5.8|us|50km NNW of Rabaul, Papua New Guinea

quakes = [ [], [], [], [] ]
for i in range(0,4):
    n = 0
    for line in lines[i]:
        if ( "#" not in line ):
            timestr = line.split('|')[1]
            qtime = datetime.datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%f')
            lat = float(line.split('|')[2])
            lon = float(line.split('|')[3])
            dep = float(line.split('|')[4])
            auth = line.split('|')[5]
            magtype  = '%4s' % line.split('|')[9]
            mag  = float(line.split('|')[10])
            quakes[i].append([qtime, lat, lon, dep, mag, magtype, auth])

print("N quakes: ", len(quakes[0]), len(quakes[1]), len(quakes[2]), len(quakes[3]) )

#----- Fetch all broadband & SMA stations in networks  AZ, CI, BK, NC, OO, US, CC, UO, UW, CN, NN, IU, II

url1 = "http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=BHE,HHE,BH1,HH1&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"
url2 = "http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=ENE,HNE&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"

# output looks like:
##Network | Station | Location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime
#AZ|BZN||BHE|33.491501|-116.667|1301.0|0.0|90.0|0.0|Streckeisen STS-2 G1/Quanterra 330 Linear Phase Be|6.29313E8|0.2|M/S|40.0|2013-10-22T19:30:00|
#AZ|BZN||HHE|33.491501|-116.667|1301.0|0.0|90.0|0.0|Streckeisen STS-2 G1/Quanterra 330 Linear Phase Be|6.29919E8|0.4|M/S|100.0|2013-10-22T19:30:00|
#AZ|CPE||BHE|32.888901|-117.105103|150.0|0.0|90.0|0.0|Streckeisen STS-2.5/Quanterra 330 Linear Phase Bel|6.28316E8|0.2|M/S|40.0|2012-12-13T21:30:00|

lines = []
f = requests.get(url1)
for lineb in f.iter_lines():
    lines.append(lineb.decode('utf-8'))
f = requests.get(url2)
for lineb in f.iter_lines():
    lines.append(lineb.decode('utf-8'))

stations = {}
stations_all = {}
for line in lines:
    if ( "#" not in line ):
        net = line.split('|')[0]
        stat = line.split('|')[1]
        loc = line.split('|')[2]
        chan = line.split('|')[3]
        lat = float(line.split('|')[4])
        lon = float(line.split('|')[5])
        nslc = net + "." + stat + "." + loc + "." + chan
        netsta = net + "." + stat
        starttime = datetime.datetime.strptime(line.split('|')[15], '%Y-%m-%dT%H:%M:%S')
        try:
            endtime = datetime.datetime.strptime(line.split('|')[16], '%Y-%m-%dT%H:%M:%S')
        except:
            endtime = datetime.datetime(2599,1,1,0,0,0)
        if ( nslc in stations_all ):
            if ( starttime < stations_all[nslc][3] ):
                stations_all[nslc][0] = starttime
            if ( endtime < stations_all[nslc][4] ):
                stations_all[nslc][0] = endtime
        else:
            stations_all[nslc] = [ nslc, lat, lon, starttime, endtime ]

#----- For each station, randomly choose Nmax_per_station events from each of the 4 quake queries

distances = [ np.zeros(181), np.zeros(181), np.zeros(181), np.zeros(181) ]
for nslc in stations_all:
    check_IRIS_WS()
    time.sleep(2)  # intentional speed bump to be safe
    nslcz = nslc[:-1] + "Z"
    net = nslc.split(".")[0]
    stat = nslc.split(".")[1]
    netstat = net + '.' + stat
    loc = nslc.split(".")[2]
    chan = nslc.split(".")[3]
    chan3 = chan + "," + chan[0:2] + "Z" + "," + chan[0:2] + "N" + "," + chan[0:2] + "1" + "," + chan[0:2] + "E" + "," + chan[0:2] + "2"
    slat = stations_all[nslc][1]
    slon = stations_all[nslc][2]
    starttime = stations_all[nslc][3]
    endtime = stations_all[nslc][4]
    for i in range(0,4):
        ncount = 0
        nfailed = 0
        print("QUAKES ",i)
        quakesindicies = list(np.arange(len(quakes[i])))
        while ( ncount < Nmax_per_station and len(quakesindicies) > 0 and nfailed < 10 ):
            rr = random.randint(0,len(quakesindicies)-1)
            r = quakesindicies[rr]
            qtime = quakes[i][r][0]
            if ( qtime < starttime or qtime > endtime ):
                quakesindicies.remove(r)
            else:
                Time1 = timeit.default_timer()
                strqtime = qtime.strftime("%Y.%m.%dT%H.%M.%S")
                qlat = quakes[i][r][1]
                qlon = quakes[i][r][2]
                dep = quakes[i][r][3]
                mag = quakes[i][r][4]
                dist = locations2degrees(slat, slon, qlat, qlon)
                distances[i][int(round(dist))] += 1
                TT_P = get_TT(dep,dist)
                time_P = qtime + timedelta(seconds = TT_P)
                TP1 = UTCDateTime(time_P - timedelta(seconds = TafterP ))
                TP2 = UTCDateTime(time_P + timedelta(seconds = TbeforeP ))
                TP1write = UTCDateTime(time_P - timedelta(seconds = 5 ))
                TP2write = UTCDateTime(time_P + timedelta(seconds = 10 ))
                TP3 = UTCDateTime(time_P - timedelta(seconds = 30 ))
                TP4 = UTCDateTime(time_P + timedelta(seconds = 45 ))
                try:
                    print('Downloading: ', nslcz, TP1, TP2, ' M', mag, ' dist= ', str(int(dist)), ' dep= ', dep )
                    time.sleep(0.11)  # too many requests/sec = your IP is put in pentaly box for 20 sec!
                    nfailed = nfailed + 1
                    st, strawplot, stAcc, stVel = [], [], [], []
                    st = client.get_waveforms(network=net, station=stat, location=loc,
                                      channel=chan3, starttime=TP1, endtime=TP2,
                                      minimumlength = minlen, longestonly = True,
                                      attach_response = True )
                    time.sleep(0.11)
                    inv = []
                    inv = client.get_stations(network=net,station=stat,location=loc,channel=chan3,starttime=TP1,endtime=TP2,level='response')
                    nfailed = -10   # there's at least some data, give the nslc a chance
                    if ( len(st) == 3 and st[2].stats.npts >= int(minlen/st[2].stats.delta )  ):
                        st.detrend(type='demean')
                        #----- check for bitnoise
                        if ( max(abs(st[0].data)) < 20 or max(abs(st[1].data)) < 20 or max(abs(st[2].data)) < 20 ):
                            iskip = 1/0
                        strawplot = st.copy()
                        if ( st[0].stats.sampling_rate != sample_rate ):
                            st.interpolate(sample_rate)
                        process = psutil.Process(os.getpid())
                        #print('MEMORY usage: ',int(100*process.memory_info().rss/(1024*1024*1024))/100.,'GB' )
                        #----- Prepare trace for writing.  Filter, demean, taper, make ACC & VEL traces
                        #      performed on each trace (segment) in the stream.
                        stVel = st.copy()
                        stVel.remove_sensitivity(inv)
                        stVel.filter('highpass', freq = HPcorner, corners = 2, zerophase = False )
                        if ( chan[1:2] == 'N'):
                            stVel.integrate(method='cumtrapz')

                        #------ Calculate if Z component would trigger EPIC
                        for itr in range(0,3):
                            if ( st[itr].stats.channel[2:3] == 'Z' ):
                                tr, trVel, trAcc, trVel3Hz = [], [], [], []
                                tr = st[itr]
                                trVel3Hz = raw_trace_to_ground_motion_filtered_pruned(tr,TP3,TP4,"Vel",0,0,3.0,0,0,inv).copy()
                                stalta = classic_sta_lta(trVel3Hz,ista,ilta)
                                datastalta = []
                                datastalta = np.concatenate((datastalta,stalta),axis=0)

                                #----- perform minimal quality checks.  1d Parrival time is at npts=3000
                                if ( max(datastalta[2500:4000]) < MinSTALTA ):
                                    iskip = 1/0
                                if ( max(datastalta[2500:4000]) / max(datastalta[0:2000]) < 1.33 ):
                                    iskip = 1/0

                                #----- shift to align on first STA/LTA > 20, or peak(STA/LTA)
                                istalta = 0
                                if ( max(datastalta[2500:4000]) >= 20 ):
                                    for istalta in range(2500,4000):
                                        if ( datastalta[istalta] >= 20 ):
                                            break
                                    ishift = istalta - 3000
                                else:
                                    ishift = np.argmax(datastalta[2500:4000]) - 500

                                #----- apply STA/LTA based shift
                                TP3 = TP3 + ( ishift / sample_rate ) + 5.
                                TP4 = TP4 + ( ishift / sample_rate ) - 10.
                                strawplot.trim(starttime=TP3,endtime=TP4)
                                TP1write = TP1write + ( ishift / sample_rate )
                                TP2write = TP2write + ( ishift / sample_rate )

                                #----- get Acc, Vel traces.
                                trVel = raw_trace_to_ground_motion_filtered_pruned(tr,TP3,TP4,"Vel",0,0,HPcorner,0,0,inv).copy()
                                trAcc = raw_trace_to_ground_motion_filtered_pruned(tr,TP3,TP4,"Acc",0,0,HPcorner,0,0,inv).copy()

                                #----- calculate Trigger label Yes/No. STA/LTA > 20 AND max(abs(Acc)) > 0.000031623 m/s^2
                                maxstalta = max(datastalta[2500+ishift:4000+ishift])
                                strmaxstalta = str(int(maxstalta))
                                if ( maxstalta >= 20 and max(abs(trAcc.data[2500+ishift:4000+ishift])) > 0.000031623 ):
                                    stryesno = "YES"
                                else:
                                    stryesno = "NO"

                                #----- Write output into local dir ./TELESEISMS
                                locwrite = st[0].stats.location
                                if ( locwrite == '' ): locwrite = '--'
                                name = netstat + "." + locwrite + "." + st[0].stats.channel[0:2] + "." + strqtime + ".M" + \
                                       str(int(10*mag)/10.) + ".d" + str(int(dist)) + ".z" + str(int(dep)) + ".Lat" + \
                                       str(qlat) + ".Lon" + str(qlon) + ".stalta" + strmaxstalta + ".Trigger_" + stryesno
                                stwrite = stVel.copy()
                                stwrite.trim( starttime=TP1write, endtime=TP2write)
                                stwrite.write('TELESEISMS/' + str(i) + '/' + name + '.hdf5', format='H5')
                                stwrite.write('TELESEISMS/' + str(i) + '/' + name + '.mseed', format='MSEED')

                                Time2 = timeit.default_timer()

                                #----- Make figures into local dir ./FIGURES
                                figname = "FIGURES/" + str(i) + "/" + netstat + "." + locwrite + "." + \
                                          st[0].stats.channel[0:2] + "Z." + strqtime + ".M" + str(int(10*mag)/10.) + ".d" + \
                                          str(int(dist)) + ".z" + str(int(dep)) + ".Lat" + str(qlat) + ".Lon" + str(qlon) + \
                                          ".stalta" + strmaxstalta + ".Trigger_" + stryesno + ".png"
                                fig = plt.figure(figsize=(8,7))

                                #-- Raw seismogram
                                ax = fig.add_subplot(4, 1, 1)
                                ax.plot(strawplot[itr].times("matplotlib"), strawplot[itr].data, "k-")
                                title = nslcz + "  " + strqtime + "  M" + str(int(10*mag)/10.) + "  z=" + str(int(dep)) + \
                                        "  dist=" + str(int(dist)) + "  Trig: " + stryesno
                                ax.set_title(title)
                                ax.xaxis_date()
                                ax2 = ax.twinx()
                                ax2.set_ylabel('Raw')
                                ax2.set(yticklabels=[])

                                #-- Sensitivity corrected, HP filtered, Acceleration trace w Trigger threshold
                                ax = fig.add_subplot(4, 1, 2)
                                ax.plot(trAcc.times("matplotlib"), trAcc.data, "b-")
                                ax.plot(trAcc.times("matplotlib"), 0.000031623*np.ones(trAcc.stats.npts), "r-")
                                ax.xaxis_date()
                                ax2 = ax.twinx()
                                ax2.set_ylabel('Acc >0.075 Hz')
                                ax2.set(yticklabels=[])

                                #-- What output file will look like: Sensitivity corrected, HP filtered, Vel trace
                                ax = fig.add_subplot(4, 1, 3)
                                ax.plot(trVel.times("matplotlib"), trVel.data, "k-")
                                ax.xaxis_date()
                                ax2 = ax.twinx()
                                ax2.set_ylabel('Vel >0.075 Hz')
                                ax2.set(yticklabels=[])

                                #-- STA/LTA function based on HPfiltered @ 3Hz Vel trace
                                ax = fig.add_subplot(4, 1, 4)
                                datastaltaplot = datastalta[500+ishift:6500+ishift]
                                times = np.arange(len(datastaltaplot))/100.
                                ax.plot(times, datastaltaplot, "r-")
                                ax.set_ylim(-0.5,21)
                                ax2 = ax.twinx()
                                ax2.set_ylabel('STA/LTA')
                                ax2.set(yticklabels=[])
                                plt.savefig(figname)
                                plt.close(fig)

                                Time3 = timeit.default_timer()
                                print("TIMES  to calculate/write: ",Time2 - Time1, "  to plot: ", Time3-Time2)

                                ncount += 1
                except:
                    pass

                quakesindicies.remove(r)


