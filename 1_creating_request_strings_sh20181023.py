

import pandas as pd
import random
import requests
import json
import time

REQUESTS_PER_DAY = 100
sh_key = "insert_key"


import pandas as pd
import random
import requests
import json
import time



REQUESTS_PER_DAY = 100
sh_key = "insert key"
location = input("Ottawa (o) or Vancouver (v)? ")


#   read-in sets of 10 to send
sets = pd.read_excel("all_combos3_o.xlsx")
#   read-in FIDs with lat-lon info
#all_points = pd.read_excel("cda_greater_vancouver_centroid.xls")
all_points = pd.read_excel("cda_ottawa_gat_points.xls")

#df_for_requests = sets.head(REQUESTS_PER_DAY)
df_for_requests = sets


transport_method = 'driving-car' # ALL OPTIONS: driving-car; driving-hgv; cycling-regular; cycling-safe; cycling-mountain; cycling-tour; cycling-electric; foot-walking; foot-hiking; wheelchair
metrics = "distance" #%7Cduration alternatively can just keep 'distance' or 'duration'
all_requests = []

for i, row in df_for_requests.iterrows():
    temp_df = pd.DataFrame(data = row.tolist(), columns = ['FID'])
    temp_df = temp_df.merge(all_points[['FID', 'LONGITUDE', 'LATITUDE']], on = 'FID', how = 'left')

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
ar.to_csv("all_requests_{}.csv".format(location))

#       CURRENTLY CODED FOR VANCOUVER


#   read-in sets of 10 to send
sets = pd.read_excel("all_combos3.xlsx")
#   read-in FIDs with lat-lon info
all_points = pd.read_excel("cda_greater_vancouver_centroid.xls")

#df_for_requests = sets.head(REQUESTS_PER_DAY)
df_for_requests = sets


transport_method = 'driving-car' # ALL OPTIONS: driving-car; driving-hgv; cycling-regular; cycling-safe; cycling-mountain; cycling-tour; cycling-electric; foot-walking; foot-hiking; wheelchair
metrics = "distance" #%7Cduration alternatively can just keep 'distance' or 'duration'
all_requests = []

for i, row in df_for_requests.iterrows():
    temp_df = pd.DataFrame(data = row.tolist(), columns = ['FID'])
    temp_df = temp_df.merge(all_points[['FID', 'LONGITUDE', 'LATITUDE']], on = 'FID', how = 'left')

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
ar.to_csv("all_requests.csv")
