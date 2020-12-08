# machine_learning_pnsn_data_set
Data set of Pwavelets and noise from PNSN and other stations for use by ML

The Trigger label:
This is based on the trigger criteria for Elarms3 (Chung et al. reference XXX).  Notable differences is that Elarms3 has many criteria for declaring a bump a trigger.  This label only uses the two primary ones: 1) whether the STA/LTA (0.05sec/5.0sec) function of 3Hz highpassed velocity data exceeds 20 and 2) if the peak amplitude exceeds 0.000031623 m/s^2.  
-E3 searches for the peak amplitude in a limited (4 sec?) window following the trigger, I'm using peak amplitude in the entire window from -5 to +10 sec.  
-E3 uses cm, I use m.
-E3 considers horizontal channels and has H/V amplitude checks, I don't.
-E3 applies a teleseismic filter using multiple narrow band filters, I don't.
-E3 checks if trigger is a boxcar, I don't.

-----------------

TLDR of data processing (see Obspy  LINK  XXXX):

st = client.get_waveforms(...starttime = -60, endtime = +60 around Pwave, minimumlength = 119)
st.detrend(type='demean')
if ( st[0].stats.sampling_rate != 100 ):  # make sure sampling rate == 100 Hz
    st.interpolate(100)
st.remove_sensitivity(inv)

STA/LTA function (only on Z component):
trVel3 = st[Z component].copy()
trVel3.slice( -30 to +45 sec)
if ( chan[1:2] == 'N'):
    trVel3.integrate(method='cumtrapz')
trVel3.filter("highpass", freq = 3.0, corners = 2, zerophase = False)
trVel3.detrend(type='demean')
stalta = classic_sta_lta(trVel3,0.05*100,5.0*100)

Noise/quality check:
if ( max(stalta[ -5 to + 10 sec]) < 3 ): skip this trace
if ( max(stalta[ -5 to + 10 sec]) / max(stalta[ -30 to -10 sec]) < 1.33 ): skip this trace

Acceleration trace to check for mininmum amplitude (in m/s^2):
trAcc = st[Z component].copy()
trAcc.filter('highpass', freq = 0.075, corners = 2, zerophase = False )
if ( chan[1:2] == 'H'):
    trAcc.differentiate(method='gradient')
trAcc.slice( -30 to +45 sec)
trAcc.filter("highpass", freq = 0.075, corners = 2, zerophase = False)
trAcc.detrend(type='deman')

if ( max(stalta) > 20 and max(abs(trAcc.data)) > 0.000031623 ):
    TriggerLabel = 'YES'
else:
    TriggerLabel = 'NO'

Output file (in units of m/sec):
stVel = st.copy()
stVel.filter('highpass', freq = 0.075, corners = 2, zerophase = False )
if ( chan[1:2] == 'N'):  # integrate strong motion channels from native to VEL
    stVel.integrate(method='cumtrapz')
stVel.trim( -5 to +10 sec around STA/LTA trigger estimated P arrival)
write output



Data are initially aligned on the predicted P wave arrival using iasp91.  From ~90 to 107 degrees P/Pdiff is the time given.  From 107 to 180 the earliest PKP arrival is used.  The data are then shifted according the STA/LTA ratio using a window of -5 to +10 seconds around the predicted P-arrival.  The shift corresponds to when the STA/LTA first exceeds 20.  If it does not exceed 20 in the window, then the data are shifted to align on the maximum of the STA/LTA function.  The window for shfited data is -5 to +10 sec.

Output files (in units of m/s, 100 Hz sampling):
Files of P-waves are given in either mseed or HDF5 format.  In each file, all 3 components are present and are aligned from -5 to +10 sec of the P-wave arrival.
