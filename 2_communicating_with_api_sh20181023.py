

import pandas as pd
import requests
import json
import time


sh_key = "5b3ce3597851110001cf6248b4ada0ce59414b1fb627a1032b519447"
##### NEED TO CREATE A FILE WITH FIDS AND 'SNAPPED' COORDINATES

####    WORKING WITH API
ar = pd.read_csv("all_requests.csv")
ar = ar.head(5)


all_json_data = []
all_fids = []
for i,row in ar.iterrows():
    req = row['request_string']
    fids = row.tolist()[2:]

    try:
        r = requests.get(req)
        json_data = json.loads(r.text)
        all_json_data.append(json_data)
        all_fids.append(fids)
    except:
        print("some error")

t_dp = []
for z in range(0, len(all_json_data)):
    js = all_json_data[z]
    for i in range(0, len(js['sources'])):
        for j in range(0, len(js['destinations'])):
            t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j], all_fids[z][i], all_fids[z][j]])
final_df = pd.DataFrame(data = t_dp, columns = ['source_snapped_coords', 'destination_coords', 'network_distance', 'FID_source', 'FID_dest'])
final_df.to_excel("final_df.xlsx")


'''
r = requests.get(s1+s2+s3)
json_data = json.loads(r.text)
    all_json_data.append(json_data)

t_dp = []
for js in all_json_data:
    for i in range(0, len(js['sources'])):
        for j in range(0, len(js['destinations'])):
            t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j]])

final_df = pd.DataFrame(data = t_dp)
final_df.to_excel("final_df.xlsx")

'''













'''


###
def some(x,n):
    return x.loc[random.sample(x.index.tolist(),n)]

# read in example list of 200 lat-lon pairs
pairs = pd.read_excel("INPUT_distance_matrix_for_meeting.xlsx")

all_pair_combinations = []
for i in pairs['ORIG_FID'].tolist():
    for j in pairs['ORIG_FID'].tolist():
        all_pair_combinations.append([i,j])

df_pair_combinations = pd.DataFrame(data = all_pair_combinations, columns = ['FID1', 'FID2'])
df_pair_combinations = df_pair_combinations.merge(pairs, left_on = 'FID1', right_on = 'ORIG_FID', how = 'left')
df_pair_combinations = df_pair_combinations.merge(pairs, left_on = 'FID2', right_on = 'ORIG_FID', how = 'left')
df_pair_combinations.columns = ['FID1','FID2','drop','lon1','lat1','drop','lon2','lat2']
df_pair_combinations = df_pair_combinations[[i for i in df_pair_combinations.columns if i != 'drop']]

# reduce example sample by keeping random (for some variation) rows
sample_pairs = some(df_pair_combinations, 1000)
sample_pairs.sort_values(by = ['FID1', 'FID2'], inplace = True)

sample_pairs.to_excel('sample_pairs.xlsx')

to_send_all = []
for i, r in sample_pairs.iterrows():
    to_send_all.append([r['FID1'], r['FID2'], (r['lon1'], r['lat1']), (r['lon2'], r['lat2'])])

df_all = pd.DataFrame(data = to_send_all, columns = ['fid1', 'fid2', 'coords1', 'coords2'])
df_all.to_excel("df_all.xlsx")

print("Coordinate pairs established")

cts1 = df_all['coords1'].tolist()
cts2 = df_all['coords2'].tolist()

transport_method = 'driving-car' # ALL OPTIONS: driving-car; driving-hgv; cycling-regular; cycling-safe; cycling-mountain; cycling-tour; cycling-electric; foot-walking; foot-hiking; wheelchair
metrics = "distance" #%7Cduration alternatively can just keep 'distance' or 'duration'

all_requests = []
all_json_data = []

s1 = "https://api.openrouteservice.org/matrix?&api_key={}&profile={}".format(sh_key, transport_method)

for i in range(0, 400, 10):#len(cts1), 10):
    print("pull number:  ", i//10 + 1)
    tcts1 = cts1[i:i+10]
    tcts2 = cts2[i:i+10]

    c1 = str(tcts1[0][0]) + "," + str((tcts1[0][1]))
    c2 = str(tcts2[0][0]) + "," + str((tcts2[0][1]))

    s2 = "&locations={}|{}".format(c1,c2)
    for xc in range(1, len(tcts1)):
        c1b = str(tcts1[xc][0]) + "," + str((tcts1[xc][1]))
        c2b = str(tcts2[xc][0]) + "," + str((tcts2[xc][1]))
        #print(c1b)
        #print(c2b)
        s2 = s2 + "|" + c1b + "|" + c2b


    s3 = "&metrics={}".format(metrics)

    print()

    r = requests.get(s1+s2+s3)
    all_requests.append(str(s1+s2+s3))

    json_data = json.loads(r.text)
    all_json_data.append(json_data)


ar = pd.DataFrame(data = all_requests)
ar.to_csv("all_requests.csv")


t_dp = []
for js in all_json_data:
    for i in range(0, len(js['sources'])):
        for j in range(0,len(js['destinations'])):
            t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j]])

final_df = pd.DataFrame(data = t_dp)
final_df.to_excel("final_df.xlsx")
#print(json_data['sources'])

#print(json_data['destinations'])
'''


'''
r = requests.get("https://api.openrouteservice.org/matrix?api_key=5b3ce3597851110001cf6248b4ada0ce59414b1fb627a1032b519447&profile=driving-car&locations=9.970093,48.477473%7C9.207916,49.153868%7C37.573242,55.801281%7C115.663757,38.106467")
#request.open('GET', 'https://api.openrouteservice.org/matrix?api_key=5b3ce3597851110001cf6248b4ada0ce59414b1fb627a1032b519447&profile=driving-car&locations=9.970093,48.477473%7C9.207916,49.153868%7C37.573242,55.801281%7C115.663757,38.106467');
json_data = json.loads(r.text)
for i in json_data:
    print(json_data[i])
    print()
#print(json_data)


to_send = pd.read_excel("to_send.xlsx")
# ensure this file has the following columns:
#   1   containing lists of 10 FIDs
#   2   containing lists of lat-lon coords for each FID

coords_to_send = to_send['coords_list'].tolist()

transport_method = 'driving-car' # ALL OPTIONS: driving-car; driving-hgv; cycling-regular; cycling-safe; cycling-mountain; cycling-tour; cycling-electric; foot-walking; foot-hiking; wheelchair
metrics = "distance%7Cduration" # alternatively can just keep 'distance' or 'duration'

for cts in coords_to_send:
    s1 = "https://api.openrouteservice.org/matrix?api_key={}&profile={}".format(sh_key, transport_method)
    s2 = "&locations={}%2C{}".format(cts[0][0], cts[[0][1])
                                     #s2 = "&locations={}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}%7C{}%2C{}".format()
    for c in cts[1:]:
        s2 = s2+"%7C{}%2C{}".format(c[0], c[1])
    s3 = "&metrics={}".format(metrics)

    print(s1+s2+s3)
'''
