#!/home/ahutko/anaconda3/bin/python

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

figdir = "/home/ahutko/proj/FOR_MEN/FIGURES/"

distances = []
mags = []
staltas = []
deps = []
minmag = 9.9
maxmag = 0
for n in [ 0, 1 , 2, 3 ]:
    distances.append([])
    mags.append([])
    staltas.append([])
    deps.append([])
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
        distances[n].append(dist)
        mags[n].append(mag)
        staltas[n].append(min(stalta,75))
        deps[n].append(dep)

#----- histogram of distances
nbins = 18
x = distances
plt.rcParams['font.size'] = '6'
fig, axs = plt.subplots(2, 2)
axs[0,0].set_title('M4-5 West Coast')
axs[0,0].hist(x[0],nbins,label=('n='+str(len(x[0]))))
axs[0,0].legend(prop={'size': 8})

axs[0,1].set_title('North Am. M>5')
axs[0,1].hist(x[1],nbins,label=('n='+str(len(x[1]))))
axs[0,1].legend(prop={'size': 8})

axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].hist(x[2],nbins,label=('n='+str(len(x[2]))))
axs[1,0].legend(prop={'size': 8})

axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].hist(x[3],nbins,label=('n='+str(len(x[3]))))
axs[1,1].legend(prop={'size': 8})
fig.suptitle('Distance',fontsize=12)
figname = 'Distances_histogram.png'
plt.savefig(figname, dpi=180)

#----- histogram of magnitudes
x = mags
fig, axs = plt.subplots(2, 2)
axs[0,0].hist(x[0],int(10*(max(x[0]) - min(x[0]))),label=('n='+str(len(x[0]))))
axs[0,0].set_title('M4-5 West Coast')
axs[0,0].legend(prop={'size': 8})

axs[0,1].hist(x[1],int(10*(max(x[1]) - min(x[1]))),label=('n='+str(len(x[1]))))
axs[0,1].set_title('North Am. M>5')
axs[0,1].legend(prop={'size': 8})

axs[1,0].hist(x[2],int(10*(max(x[2]) - min(x[2]))),label=('n='+str(len(x[2]))))
axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].legend(prop={'size': 8})

axs[1,1].hist(x[3],int(10*(max(x[3]) - min(x[3]))),label=('n='+str(len(x[3]))))
axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].legend(prop={'size': 8})
fig.suptitle('Magnitudes',fontsize=12)
figname = 'Mags_histogram.png'
plt.savefig(figname, dpi=180)

#----- histogram of STA/LTA ratios
nbins = 40
x = staltas
fig, axs = plt.subplots(2, 2)
axs[0,0].hist(x[0],nbins,label=('n='+str(len(x[0]))))
axs[0,0].set_title('M4-5 West Coast')
axs[0,0].legend(prop={'size': 8})

axs[0,1].hist(x[1],nbins,label=('n='+str(len(x[1]))))
axs[0,1].set_title('North Am. M>5')
axs[0,1].legend(prop={'size': 8})

axs[1,0].hist(x[2],nbins,label=('n='+str(len(x[2]))))
axs[1,0].set_title('Global z<100 km M>=6')
axs[1,0].legend(prop={'size': 8})

axs[1,1].hist(x[3],nbins,label=('n='+str(len(x[3]))))
axs[1,1].set_title('Global z>100 km M>=6')
axs[1,1].legend(prop={'size': 8})
fig.suptitle('STA/LTA ratio',fontsize=12)
figname = 'Staltas_histogram.png'
plt.savefig(figname, dpi=180)


