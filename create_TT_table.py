#!/home/ahutko/anaconda3/bin/python

'''
Example query using the NEIC API:
https://prod-earthquake.cr.usgs.gov/fdsnws/event/1/query?format=xml&starttime=2014-01-01&endtime=2014-01-02&minmagnitude=5&format=text

output of NEIC API:
#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName
usc000lvb5|2014-01-01T16:03:29.000|-13.8633|167.249|187|us|us|us|usc000lvb5|mww|6.5|us|32km W of Sola, Vanuatu
usc000lv5e|2014-01-01T00:01:16.610|19.0868|120.2389|10.07|us|us|us|usc000lv5e|mb|5.1|us|76km NNW of Davila, Philippines
'''

import numpy as np
from obspy.taup import TauPyModel
model = TauPyModel(model="iasp91")

Pvel = 5.

depths = [ 1, 10, 20, 30, 35, 40, 50, 70, 90, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700 ]

print(depths)
for idist in range(0,181):
    dist = idist*1.
    TTs = {}
    for depth in depths:
        arrivals = []
        if ( dist < 95. ):
            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["P"])
#            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["pP","sP"])
        elif ( dist >= 95. and dist < 115. ):
            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["P","Pdiff"])
#            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["pP","pPdiff","sP","sPdiff"])
        else:
            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["PKP","PKIKP"])
#            arrivals = model.get_travel_times(source_depth_in_km=depth,distance_in_degree=dist,phase_list=["pPKP","pPKIKP","sPKP","sPKIKP"])
        TT = 9e9
        for iTT in range(0,len(arrivals)):
            if ( arrivals[iTT].time < TT ):
                TT = arrivals[iTT].time
        if ( len(arrivals) == 0 ):
            distXY = dist*111.19
            distTT = np.sqrt((distXY*distXY) + (depth*depth))
            if ( distXY < 3 ):
                TT = distTT/Pvel
            elif ( distXY < 10 ):
                TT = distTT/7.2
            elif ( distXY < 20 ):
                TT = distTT/8.3
            elif ( distXY < 50 ):
                TT = distTT/10.
            else:
                TT = distTT/12.5
#        print( depth, idist, len(arrivals), TT)
        TTs[depth] = int(TT*10)/10.
    print(idist, list(TTs.values()))


