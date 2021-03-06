#!/home/ahutko/anaconda3/bin/python

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

figdir = "/home/ahutko/proj/FOR_MEN/FIGURES/"

distances, distancesY, distancesN = [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ]
mags, magsY, magsN = [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ]
staltas, staltasY, staltasN = [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ]
deps, depsY, depsN = [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ]
minmag = 9.9
maxmag = 0
for n in [ 0, 1 , 2, 3 ]:
    dir = figdir + str(n)
    ls = os.listdir(dir)
    for fig in ls:
      if ( '.png' in fig ):
        net = fig.split('.')[0]
        sta = fig.split('.')[1]
        loc = fig.split('.')[2]
        chan = fig.split('.')[3]
        yr = int(fig.split('.')[4])
        mo = int(fig.split('.')[5])
        mag1 = fig.split('.')[9].split('M')[1]
        mag2 = fig.split('.')[10]
        mag = float(mag1 + "." + mag2 )
        if ( mag < minmag): minmag = mag
        if ( mag > maxmag): maxmag = mag
        dist = int(fig.split('.')[11].split('d')[1])
        dep = int(fig.split('.')[12].split('z')[1])
        lat1 = fig.split('.')[13].split('Lat')[1]
        lat2 = fig.split('.')[14]
        lat = float(lat1 + '.' + lat2)
        lon1 = fig.split('.')[15].split('Lon')[1]
        lon2 = fig.split('.')[16]
        lon = float(lon1 + '.' + lon2)
        stalta = int(fig.split('.')[17].split('stalta')[1])
        trig = fig.split('.')[18].split('Trigger_')[1]
        if ( trig == 'YES' ):
            distancesY[n].append(dist)
            magsY[n].append(mag)
            staltasY[n].append(min(stalta,75))
        else:
            distancesN[n].append(dist)
            magsN[n].append(mag)
            staltasN[n].append(min(stalta,75))
        distances[n].append(dist)
        mags[n].append(mag)
        staltas[n].append(min(stalta,75))
        deps[n].append(dep)

#--------- Plot stacked histograms

#----- histogram of distances
nbins = 18
x = distances
xY = distancesY
xN = distancesN
for i in range(0,4):   #--- just to make binning the same
    x[i].append(180)
    xY[i].append(180)
    xN[i].append(180)
    x[i].append(0)
    xY[i].append(0)
    xN[i].append(0)
plt.rcParams['font.size'] = '6'
fig, axs = plt.subplots(2, 2)
axs[0,0].set_title('M4-5 West Coast (plot cut off at 20k)')
axs[0,0].hist([xY[0],xN[0]],nbins,stacked=True,label=('nTrig='+str(len(xY[0])),'nTotal='+str(len(x[0]))))
axs[0,0].legend(prop={'size': 8})
axs[0,0].set_ylim([0,20000])
axs[0,0].set_ylabel('N P-wavelets')

axs[0,1].set_title('North Am. M>5')
axs[0,1].hist([xY[1],xN[1]],nbins,stacked=True,label=('nTrig='+str(len(xY[1])),'nTotal='+str(len(x[1]))))
axs[0,1].legend(prop={'size': 8})

axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].hist([xY[2],xN[2]],nbins,stacked=True,label=('nTrig='+str(len(xY[2])),'nTotal='+str(len(x[2]))))
axs[1,0].legend(prop={'size': 8})
axs[1,0].set_ylabel('N P-wavelets')
axs[1,0].set_xlabel('Degrees')

axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].hist([xY[3],xN[3]],nbins,stacked=True,label=('nTrig='+str(len(xY[3])),'nTotal='+str(len(x[3]))))
axs[1,1].legend(prop={'size': 8})
axs[1,1].set_xlabel('Degrees')
fig.suptitle('Epicentral distances',fontsize=12)
figname = 'Distances_histogram.png'
plt.savefig(figname, dpi=180)

#----- histogram of magnitudes
x = mags
xY = magsY
xN = magsN
for i in range(0,4):    #--- just to make binning the same
    xY[i].append(min(x[i]))
    xY[i].append(max(x[i]))
    xN[i].append(min(x[i]))
    xN[i].append(max(x[i]))
nbins = int(10*(max(x[0]) - min(x[0]))) +1
plt.rcParams['font.size'] = '6'
fig, axs = plt.subplots(2, 2)
axs[0,0].set_title('M4-5 West Coast')
axs[0,0].hist([xY[0],xN[0]],nbins,stacked=True,label=('nTrig='+str(len(xY[0])),'nTotal='+str(len(x[0]))))
axs[0,0].legend(prop={'size': 8})
axs[0,0].set_ylabel('N P-wavelets')

nbins = int(10*(max(x[1]) - min(x[1]))) +1
axs[0,1].set_title('North Am. M>5')
axs[0,1].hist([xY[1],xN[1]],nbins,stacked=True,label=('nTrig='+str(len(xY[1])),'nTotal='+str(len(x[1]))))
axs[0,1].legend(prop={'size': 8})

nbins = int(10*(max(x[2]) - min(x[2]))) +1
axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].hist([xY[2],xN[2]],nbins,stacked=True,label=('nTrig='+str(len(xY[2])),'nTotal='+str(len(x[2]))))
axs[1,0].legend(prop={'size': 8})
axs[1,0].set_ylabel('N P-wavelets')

nbins = int(10*(max(x[3]) - min(x[3]))) +1
axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].hist([xY[3],xN[3]],nbins,stacked=True,label=('nTrig='+str(len(xY[3])),'nTotal='+str(len(x[3]))))
axs[1,1].legend(prop={'size': 8})
fig.suptitle('Magnitudes',fontsize=12)
figname = 'Mags_histogram.png'
plt.savefig(figname, dpi=180)

#----- histogram of staltas
nbins = 18
x = staltas
xY = staltasY
xN = staltasN
for i in range(0,4):    #--- just to make binning the same
    xY[i].append(min(x[i]))
    xY[i].append(max(x[i]))
    xN[i].append(min(x[i]))
    xN[i].append(max(x[i]))
plt.rcParams['font.size'] = '6'
fig, axs = plt.subplots(2, 2)
axs[0,0].set_title('M4-5 West Coast')
axs[0,0].hist([xY[0],xN[0]],nbins,stacked=True,label=('nTrig='+str(len(xY[0])),'nTotal='+str(len(x[0]))))
axs[0,0].legend(prop={'size': 8})
axs[0,0].set_ylabel('N P-wavelets')

axs[0,1].set_title('North Am. M>5')
axs[0,1].hist([xY[1],xN[1]],nbins,stacked=True,label=('nTrig='+str(len(xY[1])),'nTotal='+str(len(x[1]))))
axs[0,1].legend(prop={'size': 8})

axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].hist([xY[2],xN[2]],nbins,stacked=True,label=('nTrig='+str(len(xY[2])),'nTotal='+str(len(x[2]))))
axs[1,0].legend(prop={'size': 8})
axs[1,0].set_ylabel('N P-wavelets')

axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].hist([xY[3],xN[3]],nbins,stacked=True,label=('nTrig='+str(len(xY[3])),'nTotal='+str(len(x[3]))))
axs[1,1].legend(prop={'size': 8})
fig.suptitle('STA/LTA ratios (saturated @75)',fontsize=12)
figname = 'Staltas_histogram.png'
plt.savefig(figname, dpi=180)

