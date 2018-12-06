

import pandas as pd
import requests
import json
import time
import datetime

location = input("London (l)\nMontreal (m)\nOttawa (o)\nToronto (t)\nVancouver (v)?    ")
MAX_DIST = float(input("Max birds-eye distance to consider:   "))
current_date = str(datetime.datetime.now()).split(' ')[0]
STOP_PULLING_AT = 2400

exists = False
# first time running, will create 'pulled_request_codes.csv' file, otherwise will read and add to existing
try:
    prc = pd.read_csv('pulled_request_codes_{}_{}.csv'.format(location, MAX_DIST))
    exists = True
except:
    print("cant find file")

if exists:
    pulled_codes = prc['request_code'].tolist()
else:
    pulled_codes = []

####    Grab the requests that haven't been pulled yet
ar = pd.read_csv("all_requests_{}_{}.csv".format(location,MAX_DIST))

not_pulled_strings = []
not_pulled_dauids = []
not_pulled_codes = []


for i, row in ar.iterrows():
    req_code = row['request_code']
    if req_code in pulled_codes:
        continue
    else:
        not_pulled_strings.append(row['request_string'])
        not_pulled_dauids.append(row.tolist()[2:-1])
        not_pulled_codes.append(req_code)


# NOW PULLING
cumu_pulls = 0
pulled_json_data = []
pulled_strings = []
pulled_dauids = []
pulled_codes = []

pull_n = 0

for ri in range(0,len(not_pulled_strings)):
    pull_n += 1
    if cumu_pulls == STOP_PULLING_AT:
        print("     --- Cumulative pulls limit hit ({})".format(cumu_pulls))
        break

    if pull_n % 40 == 0:
        time.sleep(90)

    req = not_pulled_strings[ri]
    dauid = not_pulled_dauids[ri]
    code = not_pulled_codes[ri]

    try:
        r = requests.get(req)
        json_data = json.loads(r.text)
        pulled_json_data.append(json_data)
        pulled_strings.append(req)
        pulled_dauids.append(dauid)
        pulled_codes.append(code)

    except:
        print("some error")

    cumu_pulls += 1
    if cumu_pulls % 100 == 0:
        print("cumu_pulls:", cumu_pulls)

pulled_this_time = pd.DataFrame({'pulled_strings':pulled_strings, 'pulled_dauids':pulled_dauids,'pulled_codes':pulled_codes})
prc2 = pd.DataFrame(data = pulled_codes, columns = ['request_code'])
prc2.to_csv('pulled_request_codes_{}_{}_TESTING.csv'.format(location, MAX_DIST))


t_dp = []
t_bad = []
n_good = 0
n_bad = 0

for z in range(0, len(pulled_json_data)):
    js = pulled_json_data[z]

    try:
        for i in range(0, len(js['sources'])):
            for j in range(0, len(js['destinations'])):
                t_dp.append([js['sources'][i]['location'], js['sources'][j]['location'],js['distances'][i][j], pulled_dauids[z][i], pulled_dauids[z][j]])
                n_good += 1
    except:
        print("some error part 2 for run {}".format(z))
        t_bad.append(js)
        n_bad += 1

    final_df = pd.DataFrame(data = t_dp, columns = ['source_snapped_coords', 'destination_snapped_coords', 'network_distance', 'DAUID_source', 'DAUID_dest'])

final_df.to_excel("final_df_{}_{}_{}.xlsx".format(location, MAX_DIST, current_date))
print("number of good pulls: ", n_good)
print("number of bad  pulls: ", n_bad)
