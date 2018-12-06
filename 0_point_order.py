# import necessary modules
import requests
import json
import pandas as pd
import time
import math
import os
import pickle

# user inputs: which location to run, and which maximum birds-eye distance to consider
location = input("London (l)\nMontreal (m)\nOttawa (o)\nToronto (t)\nVancouver (v)?    ")
MAX_DIST = float(input("Max birds-eye distance to consider:   "))

## user-defined functions
def degToRad(degrees):
    return degrees*math.pi / 180

def kmdist_latlong(row):
    lat1 = row['LATITUDE_x']
    lon1 = row['LONGITUDE_x']
    lat2 = row['LATITUDE_y']
    lon2 = row['LONGITUDE_y']

    EARTH_RADIUS = 6371
    dlat= degToRad(lat2-lat1)
    dlon= degToRad(lon2-lon1)

    lat1 = degToRad(lat1)
    lat2 = degToRad(lat2)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.sin(dlon/2)*math.sin(dlon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return EARTH_RADIUS*c

def c10_multiconditional(dic_single_counts, dic_pairs):
    # take key with highest value in dic_single_counts,
    t_dsc = dic_single_counts
    t_dp = dic_pairs

    chosen = []
    max_point_0 = list(filter(lambda x: x[1] == max(t_dsc.values()), t_dsc.items()))[0]
    chosen.append(max_point_0[0])
    t_dsc[chosen[-1]] = -1
    print("chosen initial :" , chosen)
    print("  initial score: ", max_point_0[-1])

    while len(chosen) < 10:
        temp_pairs = {}
        for k,v in t_dp.items():
            if v == False & v not in chosen:
                for i in chosen:
                    if k.split('.')[0] == str(i):
                        temp_pairs[k.split('.')[-1]] = temp_pairs.get(k.split('.')[-1], 0) + t_dsc[k.split('.')[-1]]
                        #print("adding ",t_dsc[k.split('.')[-1]]," to temp_pairs for", k.split('.')[-1])
                    elif k.split('.')[-1] == str(i):
                        temp_pairs[k.split('.')[0]] = temp_pairs.get(k.split('.')[0], 0) + t_dsc[k.split('.')[0]]
                        #print("adding ",t_dsc[k.split('.')[0]]," to temp_pairs for", k.split('.')[0])
            #if len(temp_pairs) < 9:
            #    print("LESS THAN 9")
        max_point_1 = list(filter(lambda x: x[1] == max(temp_pairs.values()), temp_pairs.items()))[0]
        chosen.append(max_point_1[0])
        t_dsc[max_point_1[0]] = -1
        #print("NEW CHOSEN:", chosen)
        #input("continue?")
    print("sent are:", [str(i) for i in list(set(chosen))])
    return [str(i) for i in list(set(chosen))]

##############

if location == 'l':
    ll_list = pd.read_excel('cda_centroids_london.xls')
elif location == 'm':
    ll_list = pd.read_excel('cda_centroids_montreal.xls')
elif location == 'o':
    ll_list = pd.read_excel('cda_ottawa_gat_points.xls')
elif location == 't':
    ll_list = pd.read_excel('cda_centroids_toronto.xls')
elif location == 'v':
    ll_list = pd.read_excel('cda_greater_vancouver_centroid.xls')
ll_list = ll_list[['DAUID', 'LONGITUDE', 'LATITUDE']]


all_pairs = []
all_combos = []
# creating all possible centroid-to-centroid pair combinations, prints progress every 500
for index_a, row_a in ll_list.iterrows():
    if index_a % 500 == 0:
        print("index_a:", index_a)
    for index_b, row_b in ll_list.iterrows():
        all_pairs.append([row_a['DAUID'], row_b['DAUID']])

df_all_pairs = pd.DataFrame(data = all_pairs, columns = ['dauid1', 'dauid2'])
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'dauid1', right_on = 'DAUID', how = 'left')
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'dauid2', right_on = 'DAUID', how = 'left')
df_all_pairs = df_all_pairs[['dauid1', 'dauid2', 'LONGITUDE_x', 'LATITUDE_x', 'LONGITUDE_y', 'LATITUDE_y']]
df_all_pairs['kmdist_euclid'] = df_all_pairs.apply(kmdist_latlong, axis = 1)
df_all_pairs.to_csv("all_pairs_with_distances_{}.csv".format(location))
print("Database of all pairs and euclidistances (no max distance cutoff) created and saved as .csv")
df_need = df_all_pairs[df_all_pairs['kmdist_euclid'] < MAX_DIST]
print('Database of all pairs and euclidistances (subject to max distance cutoff) created and being used')

need = {}
count = 0
for index, row in df_need.iterrows():
    need[str(int(row['dauid1'])) + '.' + str(int(row['dauid2']))] = False
    need[str(int(row['dauid2'])) + '.' + str(int(row['dauid1']))] = False
    count += 1
print("All relevant (to be pulled from API) pairs set to false")
print("Count of all possible pairs:", df_all_pairs.shape[0])
print("Count of pairs within {}km  :".format(MAX_DIST), df_need.shape[0])
### c10_multiconditional
c10_pairs_pulled = []

need_remaining = [len(need)]
c = 0
end = False
inter_i = 0
while not end:
    c+=1
    coord_counts = {}
    for k,v in need.items():
        if v == False:
            coord_counts[k.split('.')[0]] = coord_counts.get(k.split('.')[0], 0) + 1
            coord_counts[k.split('.')[-1]] = coord_counts.get(k.split('.')[-1], 0) + 1

    chosen = c10_multiconditional(coord_counts, need)
    all_combos.append(chosen)
# NEW ADDITION
    if len(all_combos) % 500 == 0:
        os.makedirs('XXXXXXXXXXXXXX'.format(location), exist_ok = True)
        filename = "all_combos_inter_{}_{}".format(location, inter_i)
        with open('XXXXXXXXXXXXXXXXXXX'.format(location, location, inter_i), 'wb') as f:
            pickle.dump(all_combos, f)
            f.close()
        inter_i += 1
        all_combos = [] # should we be using .clear()  ??
# NEW ADDITION
    for i in chosen:
        for j in chosen:
            if i+'.'+j in need.keys():
                need[i+'.'+j] = True
            if j+'.'+i in need.keys():
                need[j+'.'+i] = True
    remaining = [k for k,v in need.items() if v == False]
    need_remaining.append(len(remaining))

    print("TYPE NUMBER:                    ", "3")
    print("RUN NUMBER:                    ", c)
    print("TOTAL PAIRS PULLED:        ", need_remaining[0] - need_remaining[-1])
    print("TOTAL PAIRS REMAINING:     ", need_remaining[-1])
    print("   CHANGE THIS RUN:        ", need_remaining[-1] - need_remaining[-2])
    print()
    c10_pairs_pulled.append(need_remaining[0] - need_remaining[-1])
    end = need_remaining[-1] < 1
with open('XXXXXXXXXXXXXXX'.format(location, location, inter_i), 'wb') as f:
    pickle.dump(all_combos, f)
    f.close()

    #input("continue.....")

for_graph3 = pd.DataFrame(data = c10_pairs_pulled)
for_graph3.to_csv('for_graph3_{}.csv'.format(location))
for_graph3.to_excel('for_graph3_{}.xlsx'.format(location))

with open('XXXXXXX'.format(location, location, 0), 'rb') as f:
    in1 = pickle.load(f)
print("Reading-in all_combos_inter_{}_{}".format(location, 0))
df = pd.DataFrame(data = in1)
print("df shape after {}:   ".format(0), df.shape)
stop = False
i = 1
while not stop:
    try:
        with open('XXXXXXX'.format(location, location, i), 'rb') as f2:
            df = df.append(pd.DataFrame(data = pickle.load(f2)))
        print("Reading-in all_combos_inter_{}_{}".format(location, i))
        print("df shape after {}:   ".format(i), df.shape)
        i+=1
    except:
        print("IN THE EXCEPT BLOCK")
        stop = True

#all_combos3 = pd.DataFrame()
#all_combos3 = pd.DataFrame(data = all_combos)
df.to_csv("all_combos3_{}_{}.csv".format(location, MAX_DIST))
#all_combos3.to_excel("all_combos3_{}_{}.xlsx".format(location, MAX_DIST))

print("done running them all for location {}".format(location))


'''
for_graph = pd.DataFrame(data = [b10_pairs_pulled, b10_jlm_pairs_pulled, c10_pairs_pulled])
for_graph.to_csv("FOR_GRAPH.csv")
for_graph.to_excel("FOR_GRAPH.xlsx")
'''
