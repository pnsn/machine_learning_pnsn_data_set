# Machine Learning data sets from the PNSN, west coast, and GSN stations

There are two data sets here: 1a) non-earthquake sources picked by PNSN, e.g. avalanches and quarry blasts.  Total size is about 20,000 files with all three components of data.  1b) autopicks from deleted "subnet triggers" (candidate earthquakes) deemed not to be earthquakes, i.e. noise.  Up to 400k.  (Dec 19, 2020: still being collected)  And 2) a data set of >300k regional and teleseismic P-arrivals that is picked using an STA/LTA ratio based off of velocity data highpass filtered above 3Hz.  This is split up into West Coast, North American, Global shallow and Global deep sources.  Both data sets include strong motion and broadband data.  Only the IRIS data center was used, which limits the harvest for Southern and Northern California.  All data are: 3 components, velocity traces, sensitivity corrected, and high pass filtered above 0.075 Hz, and are windowed from -5 to +10 sec relative to the "pick" which is different between the PNSN and regional+teleseismic data sets.  This processing is specific to <a href="https://pubs.geoscienceworld.org/ssa/srl/article/90/2A/727/568236/Optimizing-Earthquake-Early-Warning-Performance">Elarms3</a>, one of the ShakeAlert algorithms.

**Download** .zip files of .hdf5, .mseed, .png files:

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_PNSN_non_earthquake_sources_HDF5.zip">MLdataset_PNSN_non_earthquake_sources_HDF5.zip 600MB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_PNSN_non_earthquake_sources_MSEED.zip">MLdataset_PNSN_non_earthquake_sources_MSEED.zip 600MB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_WestCoast_M4_to_M5_figs.zip">MLdataset_WestCoast_M4_to_M5_figs.zip 16GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_NorthAmerica_gtM5_figs.zip">MLdataset_NorthAmerica_gtM5_figs.zip 8GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_deep_gtM6_figs.zip">MLdataset_global_deep_gtM6_figs.zip 6GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_shallow_gtM6_figs.zip">MLdataset_global_shallow_gtM6_figs.zip 19GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_WestCoast_M4_to_M5_HDF5.zip">MLdataset_WestCoast_M4_to_M5_HDF5.zip 7GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_NorthAmerica_gtM5_HDF5.zip">MLdataset_NorthAmerica_gtM5_HDF5.zip 3GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_deep_gtM6_HDF5.zip">MLdataset_global_deep_gtM6_HDF5.zip 3GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_shallow_gtM6_HDF5.zip">MLdataset_global_shallow_gtM6_HDF5.zip 8GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_WestCoast_M4_to_M5_mseed.zip">MLdataset_WestCoast_M4_to_M5_mseed.zip 7GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_NorthAmerica_gtM5_mseed.zip">MLdataset_NorthAmerica_gtM5_mseed.zip 3GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_deep_gtM6_mseed.zip">MLdataset_global_deep_gtM6_mseed.zip 3GB</a>

<a href="https://seismo.ess.washington.edu/users/ahutko/ML_DATASET/MLdataset_global_shallow_gtM6_mseed.zip">MLdataset_global_shallow_gtM6_mseed.zip 8GB</a>

## PNSN non-earthquake seismic sources and deleted subnet triggers

Data set of non-seismic sources (quarry blasts, avalanches...) picked and labeled by the PNSN.  Use codes get_AQMS_non_earthquake_picks.py and get_AQMS_deleted_subnet_trigger_autopicks.py to get a list of picks then use download_AQMS_waveforms_for_ML.py to download waveform data.

Number of files for each source type (beginning to Dec 2020):

Surface events (avalanches, mostly on volcanoes), su:  1812

Thunder, th:  121

Probable blasts (quarry), px:  27786

Confirmed blasts, ex:  246

Sonic booms, sn:  190

PNSN subnet triggers are candidate events formed by AQMS that are possibly-but-not-obvious earthquakes.  What I'm calling deleted subnet triggers these candidate events that have been reviewed by a duty seismologist and deemed not to be a real earthquake.  For context, we typically pick things down to M ~1.5 if picked up on more than ~5 stations.  If one of the autopicks in the subnet trigger below happens to come from a very small very local earthquake, it's just luck, i.e. I expect this is a rare occurance.

*Deleted subnet triggers dataset:* all of the autopicks from events that have been deleted.  There are up to 400k of these, so as of Dec 19, 2020, consider this to be a growing data set periodically updated.  Coming soon.

*Non-earthquake seismic source dataset:* Usually handpicked arrivals.  For things like surface events that are usually very emergent, we typically pick the earliest arriving one, i.e. closest station, at a "meh that's about where it starts" time.  For larger surface events, multiple stations will be picked.  For many small ones, only one station will be picked.  For probable blasts, these are almost always initially treated, i.e. picked, like earthquakes.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/deleted_subnet_trigger_and_surface_event.jpg" width=1200 alt="Deleted subnet trigge and surface event examples" />

Note: There are plenty of other exotic sources not identified/included like the plentiful shots/kabooms from the Yakima Training Center as shown in this record secton of a deleted subnet trigger from Oct (18?) 2019.  This resulted in only one file (of the stations shown) and one source- the first pop at UW.MDW; the other stations are short period EHZ.  These pops have sonic moveouts.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/Yakima_Training_Center_Oct18_2019.jpg" width=700 alt="Yakima Training Center shots" />


## Regional and Teleseismic data set first P-arrivals

Data set of P-wavelets from PNSN and other stations prepared for ML.  download_P_waves_teleseisms.py was used to download these files.  It's currently hardwired for making the windows be -5 to +10 sec, but it shouldn't be too hard to fudge.

The Trigger label:
This is based on the trigger criteria for <a href="https://pubs.geoscienceworld.org/ssa/srl/article/90/2A/727/568236/Optimizing-Earthquake-Early-Warning-Performance">Elarms3</a>.  Notable differences is that Elarms3 has many criteria for declaring a bump a trigger.  The "Trigger" label here only uses the two primary ones: 1) whether the STA/LTA (0.05sec/5.0sec) function of 3Hz highpassed velocity data exceeds 20 and 2) if the peak amplitude exceeds 0.000031623 m/s^2 on sensitivity corrected acceleration traces high pass filtered above 0.075 Hz.  This is applied to data from strong motion as well as broadband stations.  All data are initially sensitivity corrected and, if needed, resampled to 100 Hz.

*Go to Shortcomings, caveats section at bottom of page to see differences w Elarms3*

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
Note: this only uses the IRIS FDSNWS client so many CI/BK/NC stations were not harvested.  The remedy is trivial, just add clients by replacing 'IRIS' with 'SCEDC' and 'NCEDC' in the obspy client line of download_P_waves_teleseisms.py.

- For 6-channel sites, I only collected the broadband data and not the strong motion data.  The result is that the remaining strong motion Pwavelets are from sites that are only 3 or 4 channels which are usually noisier than 6-channel sites.


*Broadbands:

"http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=BHE,HHE,BH1,HH1&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"

*Strong motions:

"http://service.iris.edu/fdsnws/station/1/query?level=channel&network=AZ,CI,BK,NC,OO,US,CC,UO,UW,CN,NN,IU,II&channel=ENE,HNE&starttime=2018-01-01T00:00:00&endtime=2599-01-01T00:00:00&format=text"


### Histograms of data
Histograms made using make_histogram.py.  Note there will be overlap in some of these datasets.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/Distances_histogram.png" width=550 alt="Histogram of distances" />


<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/Mags_histogram.png" width=550 alt="Histogram of magnitudes" />


<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/Staltas_histogram.png" width=550 alt="Histogram of STA/LTA ratios" />


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

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/CI.TUQ.--.BHZ.2017.04.03T17.40.18.M6.5.d143.z29.Lat-22.6784.Lon25.1558.stalta22.Trigger_YES.png" width=550 alt="Histogram of distances" />
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
- No instrument response was removed, only an overall sensitivity correction was applied.
- This only downloads data from IRIS.  To get all/more of the CI/BK/NC data, update the code to first try IRIS, then SCEDC or NCEDC.  Also, see "stations used" above regarding 6 vs 3-channel sites.
- The counter I put in to limit the number of Pwavelets for any given station to 100 had a bug and didn't get used.  The result is many stations have many more than 100 Pwavelets, not necessarily a bad thing and the end user can decide how to select their data.  Without the bug, the code randomly samples within the 4 lists of earthquake sources.
- Be careful with data from 10-30 (regional, mantle triplications) and in the neighborhood of 115 degrees where it's unclear whether Pdiff or PKP is the first significant arrival.  The predicted arrival might be more than the +/-5s that I assumed and hence the processing may not properly align on the arrival and may not get the "Trigger" label correct.  The cutoff distance for Pdiff in the travel time tables used to initially align things is 115 degrees.  A quick visual inspection of figures should help.
- Be aware that some stations have multiple locations with very similar waveforms (but from different instruments).  An example is IW.WCI.00.BHZ, IW.WCI.10.BHZ, IW.WCI.00.HHZ.
- I was a bit lazy with stations.  To form a station list I only queried stations from 2018-2020, so if there was a station that ended before 2018, it wasn't included in the data harvest.  It's very minor.  Also I ignored epochs, e.g. when a station was BHZ in older times and later got upgraded to HHZ.
- Make x-axis time in plot for the bottom STA/LTA trace go from -25 to +35 rather than 0-60; add tick mark on the other panels for pick time.  Add a 5th panel w the 3Hz highpassed vel trace?
- Elarms3 uses units of cm/s and cm/s^2.  Everything here is m/s and m/s^2.
- Elarms3 has additional criteria for determining a trigger including an H/V amplitude check, boxcar check, and multiple amplitude checks within 11 different narrow band filters.  Those have been ignored here.
- Elarms3 applies the mimimum trigger amplitude criteria (i.e. the 0.000031623 m/s^2) within 4s (I think) of the trigger defined as when STA/LTA first exceeds 20.  Here, that amplitude check is applied in the entire window of -5 to +10 sec around the STA/LTA 'pick' time.

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/BHZ_vs_HHZ.jpg" width=750 alt="Same station, BHZ and HHZ" />
Figure 5: This is an example of the same station recording the same event, but on different channels, BHZ vs HHZ.  Pay attention to the differing STA/LTA ratios.  Just an FYI...

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/CI.SLA.--.BHZ.2012.08.31T12.47.33.M7.6.d103.z28.Lat10.811.Lon126.638.stalta9.Trigger_NO.png" width=550 alt="Histogram of distances" />
Figure 6: Clealy this event would be easy to align using an STA/LTA with a longer STA window than 0.05s.  Maybe in a different, non-Elarms3-centric iteration, use an approach that take the max STA/LTA ratio of either 0.05 or 0.5 s for the STA.  And a bandpass of 0.3 - 1.0 Hz instead of a 3 Hz highpass on the velocity trace used for the STA/LTA function.  Or a real picker, or NEIC picks etc...

<img src="https://github.com/pnsn/machine_learning_pnsn_data_set/blob/main/figures/CI.SLA.--.BHZ.2020.06.18T12.49.53.M7.4.d89.z10.Lat-33.2927.Lon-177.8571.stalta22.Trigger_YES.png" width=550 alt="Histogram of distances" />
Figure 7: Clealy this event is aligned wrong since this is being tuned for EPIC triggering which has an STA/LTA ratio threshold of 20.

### Don't download data too fast!
*IRIS IP jail and intentionally slowing down code:*  be aware of IRIS webservices which will limit your performance.  If you have more than X concurrent connections, translation: if you make more than X requests from a single IP address, IRIS WS will block your IP for 20 sec.  
Avoid this by adding in a time.sleep(0.05) before any request and don't have more than 5 codes running simultaneously.  This may only be an issue at UW since the DMC is in our back yard.
