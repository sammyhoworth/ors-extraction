
#https://api.openrouteservice.org/directions?api_key=your-api-key&coordinates=8.34234%2C48.23424%7C8.34423%2C48.26424&profile=driving-car&preference=fastest&format=json&units=m&language=en&geometry=true&geometry_format=encodedpolyline&geometry_simplify=&instructions=true&instructions_format=text&roundabout_exits=&attributes=&maneuvers=&radiuses=&bearings=&continue_straight=&elevation=&extra_info=&optimized=true&options=%7B%7D&id=

import requests
import json
import pandas as pd
import time
import math
from itertools import combinations

my_key = "insert_key"
MAX_DIST = 5


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


# 2 versions of deciding 10 points to send
#   1.  take 10 points that appear most frequently in the needed pairs
#   2.  take 1 point that appears most frequently in the needed pairs,
#       and the 9 points that appear most frequently in pairs with that point
def a10(dic_single_counts, dic_pairs):
    all_vals = list(dics_single_counts.values())
    top10_counts = list(set(sorted(all_vals)[-10:]))
    coords_with_top10_val = []
    for val in top10_counts[::-1]:
        for k,v in d.items():
            if v == val:
                coords_with_top10_val.append(k)
    if len(coords_with_top10_val) > 10:
        return coords_with_top10_val[:10]
    else:
        return coords_with_top10_val

def b10(dic_single_counts, dic_pairs):
    t_dic_single_counts = dic_single_counts
    t_dic_pairs = dic_pairs

    chosen = []
    chosen_values = []

    max_point_0 = list(filter(lambda x: x[1] == max(t_dic_single_counts.values()), t_dic_single_counts.items()))[0]
    chosen.append(max_point_0[0])
    chosen_values.append(max_point_0[-1])
    t_dic_single_counts[chosen[-1]] = -1

    while len(chosen) < 10:
        temp_pairs = {}
        for k,v in t_dic_pairs.items():
            if v == False:
                if chosen[-1] == k.split('.')[0]:
                    temp_pairs[k.split('.')[-1]] = t_dic_single_counts[k.split('.')[-1]]
                elif chosen[-1] == k.split('.')[-1]:
                    temp_pairs[k.split('.')[0]] = t_dic_single_counts[k.split('.')[0]]
        #print("TPPPPP")
        #print(temp_pairs)
        #print("TPPPPP")
        max_point = list(filter(lambda x: x[1] == max(temp_pairs.values()), temp_pairs.items()))[0]
        chosen.append(max_point[0])
        chosen_values.append(max_point[-1])
        t_dic_single_counts[chosen[-1]] = -1

    return chosen

def b10_jlm(dic_single_counts, dic_pairs):
    t_dic_single_counts = dic_single_counts
    t_dic_pairs = dic_pairs

    chosen = []
    chosen_values = []

    max_point_0 = list(filter(lambda x: x[1] == max(t_dic_single_counts.values()), t_dic_single_counts.items()))[0]
    chosen.append(max_point_0[0])
    chosen_values.append(max_point_0[-1])
    t_dic_single_counts[chosen[-1]] = -1

    temp_pairs = {}
    for k,v in t_dic_pairs.items():
        if v == False:
            if chosen[-1] == k.split('.')[0]:
                 temp_pairs[k.split('.')[-1]] = t_dic_single_counts[k.split('.')[-1]]
            elif chosen[-1] == k.split('.')[-1]:
                temp_pairs[k.split('.')[0]] = t_dic_single_counts[k.split('.')[0]]
    next_nine_dic = {key: value for key, value in temp_pairs.items() if value in sorted(set(temp_pairs.values()),reverse=True)[:9]}
    next_nine = list(next_nine_dic.keys())[:9]
    print(chosen+next_nine)
    return chosen+next_nine


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
    ### STILL NEEDS WORK





def pairs_given_n_points(point_list, dic_pairs):
    # given n points in point_list, count how many pairs contain at least two of the points
    list_pairs = list(dic_pairs.keys())
    total = 0
    for p in list_pairs:
        if p.split('.')[0] in point_list and p.split('.')[-1] in point_list:
            total+=1
    return total




##############


csd = input("Which CSD? (v or o for vancouver or ottawa)")


'''
#to_exec = [""]

#ll_list = pd.read_excel('cda_ottawa_gat_points.xls')
ll_list = pd.read_excel('cda_greater_vancouver_centroid.xls')
ll_list = ll_list[['ORIG_FID', 'LONGITUDE', 'LATITUDE']]


all_pairs = []
for index_a, row_a in ll_list.iterrows():
    for index_b, row_b in ll_list.iterrows():
        all_pairs.append([row_a['ORIG_FID'], row_b['ORIG_FID']])

df_all_pairs = pd.DataFrame(data = all_pairs, columns = ['fid1', 'fid2'])
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid1', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid2', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs[['fid1', 'fid2', 'LONGITUDE_x', 'LATITUDE_x', 'LONGITUDE_y', 'LATITUDE_y']]
df_all_pairs['kmdist_euclid'] = df_all_pairs.apply(kmdist_latlong, axis = 1)

df_need = df_all_pairs[df_all_pairs['kmdist_euclid'] < MAX_DIST]

need = {}
count = 0
for index, row in df_need.iterrows():
    need[str(int(row['fid1'])) + '.' + str(int(row['fid2']))] = False
    need[str(int(row['fid2'])) + '.' + str(int(row['fid1']))] = False
    count += 1
print("All {} relevant pairs set to false".format(count))

print("Count of all possible pairs:", df_all_pairs.shape[0])
print("Count of pairs within {}km  :".format(MAX_DIST), df_need.shape[0])




# b10
b10_pairs_pulled = []
all_combos = []

need_remaining = [len(need)]
c = 0
end = False
while not end:
    c+=1
    coord_counts = {}
    for k,v in need.items():
        if v == False:
            coord_counts[k.split('.')[0]] = coord_counts.get(k.split('.')[0], 0) + 1
            coord_counts[k.split('.')[-1]] = coord_counts.get(k.split('.')[-1], 0) + 1

    chosen = b10(coord_counts, need)
    all_combos.append(chosen)
    for i in chosen:
        for j in chosen:
            if i+'.'+j in need.keys():
                need[i+'.'+j] = True
            if j+'.'+i in need.keys():
                need[j+'.'+i] = True
    remaining = [k for k,v in need.items() if v == False]
    need_remaining.append(len(remaining))

    print("TYPE NUMBER:                    ", "1")
    print("RUN NUMBER:                    ", c)
    print("TOTAL PAIRS PULLED:        ", need_remaining[0] - need_remaining[-1])
    print("TOTAL PAIRS REMAINING:     ", need_remaining[-1])
    print("   CHANGE THIS RUN:        ", need_remaining[-1] - need_remaining[-2])
    print()
    b10_pairs_pulled.append(need_remaining[0] - need_remaining[-1])
    end = need_remaining[-1] < 1

for_graph1 = pd.DataFrame(data = b10_pairs_pulled)
for_graph1.to_csv('for_graph1.csv')
for_graph1.to_excel('for_graph1.xlsx')

all_combos1 = pd.DataFrame(data = all_combos)
all_combos1.to_excel("all_combos1.xlsx")








#ll_list = pd.read_excel('cda_ottawa_gat_points.xls')
ll_list = pd.read_excel('cda_greater_vancouver_centroid.xls')
ll_list = ll_list[['ORIG_FID', 'LONGITUDE', 'LATITUDE']]

all_pairs = []
for index_a, row_a in ll_list.iterrows():
    for index_b, row_b in ll_list.iterrows():
        all_pairs.append([row_a['ORIG_FID'], row_b['ORIG_FID']])

df_all_pairs = pd.DataFrame(data = all_pairs, columns = ['fid1', 'fid2'])
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid1', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid2', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs[['fid1', 'fid2', 'LONGITUDE_x', 'LATITUDE_x', 'LONGITUDE_y', 'LATITUDE_y']]
df_all_pairs['kmdist_euclid'] = df_all_pairs.apply(kmdist_latlong, axis = 1)

df_need = df_all_pairs[df_all_pairs['kmdist_euclid'] < MAX_DIST]

need = {}
count = 0
for index, row in df_need.iterrows():
    need[str(int(row['fid1'])) + '.' + str(int(row['fid2']))] = False
    need[str(int(row['fid2'])) + '.' + str(int(row['fid1']))] = False
    count += 1
print("All {} relevant pairs set to false".format(count))

print("Count of all possible pairs:", df_all_pairs.shape[0])
print("Count of pairs within {}km  :".format(MAX_DIST), df_need.shape[0])

### b10_jlm
b10_jlm_pairs_pulled = []
all_combos = []
need_remaining = [len(need)]
c = 0
end = False
while not end:
    c+=1
    coord_counts = {}
    for k,v in need.items():
        if v == False:
            coord_counts[k.split('.')[0]] = coord_counts.get(k.split('.')[0], 0) + 1
            coord_counts[k.split('.')[-1]] = coord_counts.get(k.split('.')[-1], 0) + 1

    chosen = b10_jlm(coord_counts, need)
    all_combos.append(chosen)
    for i in chosen:
        for j in chosen:
            if i+'.'+j in need.keys():
                need[i+'.'+j] = True
            if j+'.'+i in need.keys():
                need[j+'.'+i] = True
    remaining = [k for k,v in need.items() if v == False]
    need_remaining.append(len(remaining))

    print("TYPE NUMBER:                    ", "2")
    print("RUN NUMBER:                    ", c)
    print("TOTAL PAIRS PULLED:        ", need_remaining[0] - need_remaining[-1])
    print("TOTAL PAIRS REMAINING:     ", need_remaining[-1])
    print("   CHANGE THIS RUN:        ", need_remaining[-1] - need_remaining[-2])
    print()
    b10_jlm_pairs_pulled.append(need_remaining[0] - need_remaining[-1])
    end = need_remaining[-1] < 1

for_graph2 = pd.DataFrame(data = b10_jlm_pairs_pulled)
for_graph2.to_csv('for_graph2.csv')
for_graph2.to_excel('for_graph2.xlsx')

all_combos2 = pd.DataFrame(data = all_combos)
all_combos2.to_excel("all_combos2.xlsx")

'''



if csd == 'o':
    ll_list = pd.read_excel('cda_ottawa_gat_points.xls')
elif csd == 'v':
    ll_list = pd.read_excel('cda_greater_vancouver_centroid.xls')

ll_list = ll_list[['ORIG_FID', 'LONGITUDE', 'LATITUDE']]
#ll_list = ll_list.head(150)



all_pairs = []
all_combos = []
for index_a, row_a in ll_list.iterrows():
    for index_b, row_b in ll_list.iterrows():
        all_pairs.append([row_a['ORIG_FID'], row_b['ORIG_FID']])

df_all_pairs = pd.DataFrame(data = all_pairs, columns = ['fid1', 'fid2'])
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid1', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs.merge(ll_list, left_on = 'fid2', right_on = 'ORIG_FID', how = 'left')
df_all_pairs = df_all_pairs[['fid1', 'fid2', 'LONGITUDE_x', 'LATITUDE_x', 'LONGITUDE_y', 'LATITUDE_y']]
df_all_pairs['kmdist_euclid'] = df_all_pairs.apply(kmdist_latlong, axis = 1)

df_need = df_all_pairs[df_all_pairs['kmdist_euclid'] < MAX_DIST]

need = {}
count = 0
for index, row in df_need.iterrows():
    need[str(int(row['fid1'])) + '.' + str(int(row['fid2']))] = False
    need[str(int(row['fid2'])) + '.' + str(int(row['fid1']))] = False
    count += 1
print("All {} relevant pairs set to false".format(count))

print("Count of all possible pairs:", df_all_pairs.shape[0])
print("Count of pairs within {}km  :".format(MAX_DIST), df_need.shape[0])
### c10_multiconditional
c10_pairs_pulled = []

need_remaining = [len(need)]
c = 0
end = False
while not end:
    c+=1
    coord_counts = {}
    for k,v in need.items():
        if v == False:
            coord_counts[k.split('.')[0]] = coord_counts.get(k.split('.')[0], 0) + 1
            coord_counts[k.split('.')[-1]] = coord_counts.get(k.split('.')[-1], 0) + 1

    chosen = c10_multiconditional(coord_counts, need)
    all_combos.append(chosen)
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

    #input("continue.....")

for_graph3 = pd.DataFrame(data = c10_pairs_pulled)
for_graph3.to_csv('for_graph3_{}.csv'.format(csd))
for_graph3.to_excel('for_graph3_{}.xlsx'.format(csd))

all_combos3 = pd.DataFrame(data = all_combos)
all_combos3.to_csv("all_combos3_{}.csv".format(csd))
all_combos3.to_excel("all_combos3_{}.xlsx".format(csd))

print("done running them all for csd {}".format(csd))


'''
for_graph = pd.DataFrame(data = [b10_pairs_pulled, b10_jlm_pairs_pulled, c10_pairs_pulled])
for_graph.to_csv("FOR_GRAPH.csv")
for_graph.to_excel("FOR_GRAPH.xlsx")
'''
