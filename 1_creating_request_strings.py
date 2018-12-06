

import pandas as pd
import random
import requests
import json
import time



REQUESTS_PER_DAY = 100
sh_key = "RANDOMRANDOMRANDOM"
location = input("London (l)\nMontreal (m)\nOttawa (o)\nToronto (t)\nVancouver (v)?    ")
MAX_DIST = float(input("Max birds-eye distance to consider:   "))

#   read-in sets of 10 to send
sets = pd.read_excel("all_combos3_{}_{}.csv".format(location,MAX_DIST))
#   read-in DAUIDs with lat-lon info
#all_points = pd.read_excel("cda_greater_vancouver_centroid.xls")
if location == 'l':
    all_points = pd.read_excel('cda_centroids_london.xls')
elif location == 'm':
    all_points = pd.read_excel('cda_centroids_montreal.xls')
elif location == 'o':
    all_points = pd.read_excel('cda_ottawa_gat_points.xls')
elif location == 't':
    all_points = pd.read_excel('cda_centroids_toronto.xls')
elif location == 'v':
    all_points = pd.read_excel('cda_greater_vancouver_centroid.xls')

#df_for_requests = sets.head(REQUESTS_PER_DAY)
df_for_requests = sets

print("Note that the transport_method is 'driving-car' and the metric pulled is 'distance'")
transport_method = 'driving-car' # ALL OPTIONS: driving-car; driving-hgv; cycling-regular; cycling-safe; cycling-mountain; cycling-tour; cycling-electric; foot-walking; foot-hiking; wheelchair
metrics = "distance" #%7Cduration alternatively can just keep 'distance' or 'duration'
all_requests = []

for i, row in df_for_requests.iterrows():
    temp_df = pd.DataFrame(data = row.tolist(), columns = ['DAUID'])
    temp_df = temp_df.merge(all_points[['DAUID', 'LONGITUDE', 'LATITUDE']], on = 'DAUID', how = 'left')

    lons = [i for i in temp_df['LONGITUDE'].tolist() if str(i) != "nan"]
    lats = [i for i in temp_df['LATITUDE'].tolist() if str(i) != "nan"]

    s1 = "https://api.openrouteservice.org/matrix?&api_key={}&profile={}".format(sh_key, transport_method)
    s2 = "&locations={},{}".format(lons[0],lats[0])
    for i in range(1, len(lons)):
        s2 = s2 + "|" + str(lons[i]) + "," + str(lats[i])
    s3 = "&metrics={}".format(metrics)
    all_requests.append(str(s1+s2+s3))

ar = pd.DataFrame(data = all_requests, columns = ['request_string'])
ar = ar.join(df_for_requests)
ar['request_code'] = ar.index
ar.to_csv("all_requests_{}_{}.csv".format(location, MAX_DIST))
