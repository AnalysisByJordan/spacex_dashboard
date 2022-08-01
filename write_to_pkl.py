import requests
import numpy as np
import pandas as pd
import time

url = "https://api.spacexdata.com/v3/launches"
data = requests.get(url)
print(data.status_code)
data_dict = data.json()

useable_list = []
useful_fields = ['flight_number', 'mission_name', 'upcoming', 'launch_year', 'launch_date_unix', 
                 'launch_date_utc','launch_date_local', 'is_tentative', 'launch_success', 'details']
for i in range(len(data_dict)):
    useable_dict = {}
    for field in useful_fields:
        useable_dict[field] = data_dict[i][field]
    useable_dict['rocket_name'] = data_dict[i]['rocket']['rocket_name']
    useable_dict['rocket_type'] = data_dict[i]['rocket']['rocket_type']
    useable_dict['video_link'] = data_dict[i]['links']['video_link']
    for key in data_dict[i]['rocket']['first_stage']['cores'][0].keys():
        useable_dict[key] = data_dict[i]['rocket']['first_stage']['cores'][0][key]
    pay_list = []
    for key in data_dict[i]['rocket']['second_stage']['payloads'][0].keys():
        pay_list.append(key)
    pay_list.remove('orbit_params')
    for key in pay_list:
        useable_dict[key] = data_dict[i]['rocket']['second_stage']['payloads'][0][key]
    for key in data_dict[i]['rocket']['second_stage']['payloads'][0]['orbit_params'].keys():
        useable_dict[key] = data_dict[i]['rocket']['second_stage']['payloads'][0]['orbit_params'][key]
    if data_dict[i]['rocket']['fairings'] is not None:
        for key in data_dict[i]['rocket']['fairings'].keys():
            useable_dict[key] = data_dict[i]['rocket']['fairings'][key]
    else:
        for key in data_dict[0]['rocket']['fairings'].keys():
            useable_dict[key] = np.nan
    for key in data_dict[i]['launch_site'].keys():
        useable_dict[key] = data_dict[i]['launch_site'][key]
    if data_dict[i]['launch_success'] == False:
        for key in data_dict[i]['launch_failure_details'].keys():
            useable_dict[key] = data_dict[i]['launch_failure_details'][key]
    else:
        for key in data_dict[0]['launch_failure_details'].keys():
            useable_dict[key] = np.nan   
    useable_list.append(useable_dict)

important_df = pd.DataFrame.from_dict(useable_list)
important_df

important_df = important_df.dropna(axis = 0, subset = ['site_name_long'])
important_df

def coord_get(location):
    URL = "https://en.wikipedia.org/w/api.php"
    
    TITLE_PARAMS = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": location
    }
    TITLE_R = requests.get(url=URL, params=TITLE_PARAMS)
    TITLE_DATA = TITLE_R.json() 
    title = TITLE_DATA['query']['search'][0]['title']
    

    LOC_PARAMS = {
    "action": "query",
    "format": "json",
    "titles": title,
    "prop": "coordinates"
    }
    LOC_R = requests.get(url=URL, params=LOC_PARAMS)
    LOC_DATA = LOC_R.json()
    PAGES = LOC_DATA['query']['pages']
    
    for k, v in PAGES.items():
        lat = v['coordinates'][0]['lat']
        long = v['coordinates'][0]['lon']
    
    time.sleep(.2)
    return {'lat' : lat, 'long': long}

coord_list = []
for site in important_df.site_name_long:
    coord_list.append(coord_get(site))
coord_list

important_df['coords'] = coord_list

important_df.to_pickle('data_df.pkl')