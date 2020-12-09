## machine_learning_pnsn_data_set
Data set of P-wavelets and noise from PNSN and other stations for use by ML

The Trigger label:
This is based on the trigger criteria for <a href="https://pubs.geoscienceworld.org/ssa/srl/article/90/2A/727/568236/Optimizing-Earthquake-Early-Warning-Performance">Elarms3</a>.  Notable differences is that Elarms3 has many criteria for declaring a bump a trigger.  This label only uses the two primary ones: 1) whether the STA/LTA (0.05sec/5.0sec) function of 3Hz highpassed velocity data exceeds 20 and 2) if the peak amplitude exceeds 0.000031623 m/s^2.  
-E3 searches for the peak amplitude in a limited (4 sec?) window following the trigger, I'm using peak amplitude in the entire window from -5 to +10 sec.  
-E3 uses cm, I use m.
-E3 considers horizontal channels and has H/V amplitude checks, I don't.
-E3 applies a teleseismic filter using multiple narrow band filters, I don't.
-E3 checks if trigger is a boxcar, I don't.

Histograms made using make_histogram.py


-----------------

## TLDR pseudocode of data processing (<a href="https://docs.obspy.org">Uses ObsPy https://docs.obspy.org</a>):
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

## Output .HDF5/.mseed files:
Files of P-waves are given in either mseed or HDF5 format.  In each file, all 3 components are present and are aligned from -5 to +10 sec of the P-wave arrival.  All traces are velocity in units of m/s, 100 Hz sampling.  .mseed and .hdf5 files are available <a href="https://seismo.ess.washington.edu/users/ahutko/ML_data_sets">here.</a> 

Data are initially aligned on the predicted P wave arrival using iasp91.  From ~90 to 107 degrees P/Pdiff is the time given.  From 107 to 180 the earliest PKP arrival is used.  The data are then shifted according the STA/LTA ratio using a window of -5 to +10 seconds around the predicted P-arrival.  The shift corresponds to when the STA/LTA first exceeds 20.  If it does not exceed 20 in the window, then the data are shifted to align on the maximum of the STA/LTA function.  The window for shfited data is -5 to +10 sec.

## Figures

## Shortcomings & caveats
- This only downloads data from IRIS.  To get all/more of the CI/BK/NC data, update the code to first try IRIS, then SCEDC or NCEDC.
- The counter I put in to limit the number of Pwavelets for any given station to 100 didn't had a bug and didn't work.  The result is some stations have many more than 100 Pwavelets, not necessarily a bad thing and the end user can decide how to select their data.
- For 6-channel sites, I only collected the broadband data and not the strong motion data.  The result is that the remaining strong motion Pwavelets are from sites that are only 3 or 4 channels which are usually noisier than 6-channel sites.
- Be careful with data from 10-30 (regional, mantle triplications) and bw 100-120 degrees (Pdiff/PKP) where the predicted arrival might be more than the +/-5s that I assumed and hence the processing may not properly align on the arrival and may not get the "Trigger" label correct.  A quick visual inspection can remedy this.

## Don't download data too fast!
*IRIS IP jail and intentionally slowing down code:*  be aware of IRIS webservices which will throttle your performance.  If you have more than X concurrent connections, translation: if you make more than X requests from a single IP address, IRIS WS will block your IP for 20 sec.  
Avoid this by adding in a time.sleep(0.05) before any request and don't have more than 5 codes running simultaneously.
