

import pandas as pd
import requests
import json
import time
import datetime

sh_key = "insert key"
location = input("Ottawa (o) or Vancouver (v)? ")
current_date = str(datetime.datetime.now()).split(' ')[0]
STOP_PULLING_AT = 50

exists = False
# first time running, will create 'pulled_request_codes.csv' file, otherwise will read and add to existing
try:
    prc = pd.read_csv('pulled_request_codes_{}.csv'.format(location))
    exists = True
except:
    print("cant find file")

if exists:
    pulled_codes = prc['request_code'].tolist()
else:
    pulled_codes = []


####    Grab the requests that haven't been pulled yet
ar = pd.read_csv("all_requests_{}.csv".format(location))

not_pulled_strings = []
not_pulled_fids = []
not_pulled_codes = []


for i, row in ar.iterrows():
    req_code = row['request_code']
    if req_code in pulled_codes:
        continue
    else:
        not_pulled_strings.append(row['request_string'])
        not_pulled_fids.append(row.tolist()[2:-1])
        not_pulled_codes.append(req_code)
        

# NOW PULLING
cumu_pulls = 0
pulled_json_data = []
pulled_strings = []
pulled_fids = []
pulled_codes = []

for ri in range(0,len(not_pulled_strings)):
    if cumu_pulls == STOP_PULLING_AT:
        print("     --- Cumulative pulls limit hit ({})".format(cumu_pulls))
        break

    req = not_pulled_strings[ri]
    fid = not_pulled_fids[ri]
    code = not_pulled_codes[ri]
    
    try:
        r = requests.get(req)
        json_data = json.loads(r.text)
        pulled_json_data.append(json_data)
        pulled_strings.append(req)
        pulled_fids.append(fid)
        pulled_codes.append(code)
        
    except:
        print("some error")

    cumu_pulls += 1
    if cumu_pulls % 100 == 0:
        print("cumu_pulls:", cumu_pulls)

pulled_this_time = pd.DataFrame({'pulled_strings':pulled_strings, 'pulled_fids':pulled_fids,'pulled_codes':pulled_codes})
prc2 = pd.DataFrame(data = pulled_codes, columns = ['request_code'])
prc2.to_csv('pulled_request_codes_{}_TESTING.csv'.format(location))


t_dp = []
t_bad = []
n_good = 0
n_bad = 0

cc = 0

for z in range(0, len(pulled_json_data)):
    if z % 30 == 0:
        time.sleep(120)
        print('pull number ',z)
        print("sleeping for 120 seconds")
    
    js = pulled_json_data[z]
   
    try:
        for i in range(0, len(js['sources'])):
            for j in range(0, len(js['destinations'])):
                t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j], pulled_fids[z][i], pulled_fids[z][j]])
                n_good += 1
    except:
        print("some error part 2 for run {}".format(z))
        t_bad.append(js)
        n_bad += 1

    final_df = pd.DataFrame(data = t_dp, columns = ['source_snapped_coords', 'destination_coords', 'network_distance', 'FID_source', 'FID_dest'])

final_df.to_excel("final_df_{}_{}.xlsx".format(location, current_date))
print("number of good pulls: ", n_good)
print("number of bad  pulls: ", n_bad)


    

'''
for i,row in ar.iterrows():
    if cumu_pulls == STOP_PULLING_AT:

        print("     --- Cumulative pulls hit {}".format(cumu_pulls))
        break
    
    req = row['request_string']
    fids = row.tolist()[2:]

    try:
        r = requests.get(req)
        json_data = json.loads(r.text)
        all_json_data.append(json_data)
        all_fids.append(fids)
    except:
        print("some error")

    cumu_pulls += 1
    if cumu_pulls % 100 == 0:
        print("cumu_pulls:", cumu_pulls)

t_dp = []
t_bad = []
n_good = 0
n_bad = 0
for z in range(0, len(all_json_data)):
    js = all_json_data[z]
    try:
        for i in range(0, len(js['sources'])):
            for j in range(0, len(js['destinations'])):
                t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j], all_fids[z][i], all_fids[z][j]])
                n_good+=1
    except:
        print("some error part 2 for run {}".format(z))
        t_bad.append(js)
        n_bad+=1
        
    final_df = pd.DataFrame(data = t_dp, columns = ['source_snapped_coords', 'destination_coords', 'network_distance', 'FID_source', 'FID_dest'])

final_df.to_excel("final_df_{}.xlsx".format(current_date))
print("number of good pulls: ",n_good)
print("number of bad  pulls: ",n_bad)

'''



