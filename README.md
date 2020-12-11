## machine_learning_pnsn_data_set
Data set of P-wavelets and noise from PNSN and other stations for use by ML

The Trigger label:
This is based on the trigger criteria for <a href="https://pubs.geoscienceworld.org/ssa/srl/article/90/2A/727/568236/Optimizing-Earthquake-Early-Warning-Performance">Elarms3</a>.  Notable differences is that Elarms3 has many criteria for declaring a bump a trigger.  This label only uses the two primary ones: 1) whether the STA/LTA (0.05sec/5.0sec) function of 3Hz highpassed velocity data exceeds 20 and 2) if the peak amplitude exceeds 0.000031623 m/s^2.  
-E3 searches for the peak amplitude in a limited (4 sec?) window following the trigger, I'm using peak amplitude in the entire window from -5 to +10 sec.  
-E3 uses cm, I use m.
-E3 considers horizontal channels and has H/V amplitude checks, I don't.
-E3 applies a teleseismic filter using multiple narrow band filters, I don't.
-E3 checks if trigger is a boxcar, I don't.
-add AQMS non-seismic noise sources
-add link to seismo https://seismo.ess.washington.edu/users/ahutko (tar .mseed, .hdf5, .png)
-explain naming of output files
[Go to Shortcomings, caveats section to see differences w Elarms3](#Shortcomings,-caveats,-&-things-to-fix-before-next-time)



### The 4 sub data sets of sources, 2010.1 - 2020.12
- M4.0 - M5.0 west coast:

https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=2009-12-31T23:25:00&endtime=2025-01-01T01:01:00&minlatitude=25.&maxlatitude=55.&minlongitude=-135.&maxlongitude=-100.&minmagnitude=4.0&maxmagnitude=5.0&format=text

- M5.0+ North America:

https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=2009-12-31T23:25:00&endtime=2025-01-01T01:01:00&minlatitude=20.&maxlatitude=65.&minlongitude=-165.&maxlongitude=-75.&minmagnitude=5.0&format=text

- Shallow (z < 100 km) Global M6.0+:

https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=2009-12-31T23:25:00&endtime=2025-01-01T01:01:00&minmagnitude=6.0&maxdepth=100&format=text

- Deep (z > 100 km) Global M6.0+:

https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?&starttime=2009-12-31T23:25:00&endtime=2025-01-01T01:01:00&minmagnitude=6.0&mindepth=100&format=text

### The stations used
Note: this only uses the IRIS FDSNWS client so many CI/BK/NC stations were not harvested.  For those, add in a try statement and use the SCEDC/NCEDC clients which are trivial modifications using obspy.
- For 6-channel sites, I only collected the broadband data and not the strong motion data.  The result is that the remaining strong motion Pwavelets are from sites that are only 3 or 4 channels which are usually noisier than 6-channel sites.


*Broadbands:

"http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=BHE,HHE,BH1,HH1&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"

*Strong motions:

"http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=ENE,HNE&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"


### Histograms of data
Histograms made using make_histogram.py (as of Dec 8, maybe 2/3? done collecting entire data set)

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/Distances_histogram.png" width=550 alt="Histogram of distances" />


<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/Mags_histogram.png" width=550 alt="Histogram of magnitudes" />


<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/Staltas_histogram.png" width=550 alt="Histogram of STA/LTA ratios" />


-----------------

### TLDR pseudocode of data processing (<a href="https://docs.obspy.org">Uses ObsPy https://docs.obspy.org</a>):
```
st = client.get_waveforms(...starttime = -60, endtime = +60 around Pwave, minimumlength = 119)
st.detrend(type='demean')
if ( st[0].stats.sampling_rate != 100 ):  # make sure sampling rate == 100 Hz
    st.interpolate(100)
st.remove_sensitivity(inv)

# STA/LTA function (only on Z component):
trVel3 = st[Z component].copy()
trVel3.slice( -30 to +45 sec)
if ( chan[1:2] == 'N'):
    trVel3.integrate(method='cumtrapz')
trVel3.filter("highpass", freq = 3.0, corners = 2, zerophase = False)
trVel3.detrend(type='demean')
stalta = classic_sta_lta(trVel3,0.05*100,5.0*100)

# Noise/quality check:
if ( max(stalta[ -5 to + 10 sec]) < 3 ): skip this trace
if ( max(stalta[ -5 to + 10 sec]) / max(stalta[ -30 to -10 sec]) < 1.33 ): skip this trace

# Acceleration trace to check for mininmum amplitude (in m/s^2):
trAcc = st[Z component].copy()
trAcc.filter('highpass', freq = 0.075, corners = 2, zerophase = False )
if ( chan[1:2] == 'H'):
    trAcc.differentiate(method='gradient')
trAcc.slice( -30 to +45 sec)
trAcc.filter("highpass", freq = 0.075, corners = 2, zerophase = False)
trAcc.detrend(type='deman')

# Trigger label:
if ( max(stalta) > 20 and max(abs(trAcc.data)) > 0.000031623 ):
    TriggerLabel = 'YES'
else:
    TriggerLabel = 'NO'

# Output file (in units of m/sec):
stVel = st.copy()
stVel.filter('highpass', freq = 0.075, corners = 2, zerophase = False )
if ( chan[1:2] == 'N'):  # integrate strong motion channels from native to VEL
    stVel.integrate(method='cumtrapz')
stVel.trim( -5 to +10 sec around STA/LTA trigger estimated P arrival)
write output
```

### Output .HDF5/.mseed files:
Files of P-waves are given in either mseed or HDF5 format.  In each file, all 3 components are present and are aligned from -5 to +10 sec of the STA/LTA 'picked' P-wave arrival.  All traces are velocity in units of m/s, 100 Hz sampling.  .mseed and .hdf5 files are available <a href="https://seismo.ess.washington.edu/users/ahutko/ML_data_sets">here.</a> 

Data are initially aligned on the predicted P wave arrival using iasp91.  From ~90 to 107 degrees P/Pdiff is the time given.  From 107 to 180 the earliest PKP arrival is used.  The data are then shifted according the STA/LTA ratio using a window of -5 to +10 seconds around the predicted P-arrival.  The shift corresponds to when the STA/LTA first exceeds 20.  If it does not exceed 20 in the window, then the data are shifted to align on the maximum of the STA/LTA function.  The window for shfited data is -5 to +10 sec.

### Figures
For each output file, there is an associated figure like this one:

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/CI.TUQ.--.BHZ.2017.04.03T17.40.18.M6.5.d143.z29.Lat-22.6784.Lon25.1558.stalta22.Trigger_YES.png" width=550 alt="Histogram of distances" />
The four panels from top to bottom show:

- The raw trace in counts

- The sensitivity-corrected acceleration trace high-pass filtered above 0.075 Hz. This is used for Trigger labeling, the red line is the minimum Acc threshold for trigging EPIC (0.000031623 m/s^2).  Units are m/s^2.

- The sensitivity-corrected velocity trace high-pass filtered above 0.075 Hz (This is the output file).  Units are m/s.

- The STA/LTA function which uses a (not shown) velocity trace highpass filtered above 3 Hz.

These figures are aligned with the STA/LTA 'pick' time at 25 sec in the bottom panel.  The output files are from -5 to +10 sec of this time (20 - 35 sec in this plot).

### Filenames for figures and output files:

d = distance, z = depth in km, Lat, Lon, max(STA/LTA ratio from -5 to +10 sec around pick time.

Trigger: does the trace have STA/LTA ratio > 20 AND is peak amplitude on Acc trace > 0.000031623 m/s^2.

```
CI.CIA.--.HHZ.2019.12.03T08.46.35.M6.0.d69.z38.Lat-18.5042.Lon-70.576.stalta11.Trigger_NO.png
CI.CIA.--.HH.2019.12.03T08.46.35.M6.0.d69.z38.Lat-18.5042.Lon-70.576.stalta11.Trigger_NO.hdf5
CI.CIA.--.HH.2019.12.03T08.46.35.M6.0.d69.z38.Lat-18.5042.Lon-70.576.stalta11.Trigger_NO.mseed
```

### Shortcomings, caveats, & things to fix before next time
- This only downloads data from IRIS.  To get all/more of the CI/BK/NC data, update the code to first try IRIS, then SCEDC or NCEDC.  Also, see "stations used" above regarding 6 vs 3-channel sites.
- The counter I put in to limit the number of Pwavelets for any given station to 100 had a bug and didn't get used.  The result is many stations have many more than 100 Pwavelets, not necessarily a bad thing and the end user can decide how to select their data.  Without the bug, the code randomly samples within the 4 lists of earthquake sources.
- Be careful with data from 10-30 (regional, mantle triplications) and bw ~110-120 degrees where it's unclear whether Pdiff or PKP is the first significant arrival.  The predicted arrival might be more than the +/-5s that I assumed and hence the processing may not properly align on the arrival and may not get the "Trigger" label correct.  The cutoff distance for Pdiff in the travel time tables used to initially align things is 115 degrees.  A quick visual inspection of figures should help.
- Be aware that some stations have multiple locations with very similar waveforms (but from different instruments).  An example is IW.WCI.00.BHZ, IW.WCI.10.BHZ, IW.WCI.00.HHZ.
- I was a bit lazy with stations.  To form a station list I only queried stations from 2018-2020, so if there was a station that ended before 2018, it wasn't included in the data harvest.  It's very minor.  Also I ignored epochs, e.g. when a station was BHZ in older times and later got upgraded to HHZ.
- Make x-axis time in plot for the bottom STA/LTA trace go from -25 to +35 rather than 0-60; add tick mark on the other panels for pick time.  Add a 5th panel w the 3Hz highpassed vel trace?
- Elarms3 uses units of cm/s and cm/s^2.  I use m/s and m/s^2.
- Elarms3 has additional criteria for determining a trigger including an H/V amplitude check, boxcar check, and multiple amplitude checks within 11 different narrow band filters.  Those have been ignored here.
- Elarms3 applies the mimimum trigger amplitude criteria (i.e. the 0.000031623 m/s^2) within 4s (I think) of the trigger defined as when STA/LTA first exceeds 20.  Here, that amplitude check is applied in the entire window of -5 to +10 sec around the STA/LTA 'pick' time.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/BHZ_vs_HHZ.jpg" width=750 alt="Same station, BHZ and HHZ" />
Figure 5: This is an example of the same station recording the same event, but on different channels, BHZ vs HHZ.  Pay attention to the differing STA/LTA ratios.  Just an FYI...

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/CI.SLA.--.BHZ.2012.08.31T12.47.33.M7.6.d103.z28.Lat10.811.Lon126.638.stalta9.Trigger_NO.png" width=550 alt="Histogram of distances" />
Figure 6: Clealy this event would be easy to align using an STA/LTA with a longer STA window than 0.05s.  Maybe next iteration, use an approach that take the max STA/LTA ratio of either 0.05 or 0.5 s for the STA.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/CI.SLA.--.BHZ.2020.06.18T12.49.53.M7.4.d89.z10.Lat-33.2927.Lon-177.8571.stalta22.Trigger_YES.png" width=550 alt="Histogram of distances" />
Figure 7: Clealy this event is aligned wrong since this is being tuned for EPIC triggering which has an STA/LTA ratio threshold of 20.

### Don't download data too fast!
*IRIS IP jail and intentionally slowing down code:*  be aware of IRIS webservices which will throttle your performance.  If you have more than X concurrent connections, translation: if you make more than X requests from a single IP address, IRIS WS will block your IP for 20 sec.  
Avoid this by adding in a time.sleep(0.05) before any request and don't have more than 5 codes running simultaneously.
