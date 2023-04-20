import datetime

from pathlib import Path
import requests
import json
import pandas as pd
from app.modules.querying import generate_q_url
import datetime as dt
from pytz import timezone

BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/?'
search_dict = {
    'dataset': 'velib-disponibilite-en-temps-reel',
    'q': '',
    'rows': -1,
    'facet': []
}

def convert_my_iso_8601(iso_8601, tz_info):
    assert iso_8601[-1] == 'Z'
    iso_8601 = iso_8601[:-1] + '000'
    iso_8601_dt = dt.datetime.strptime(iso_8601, '%Y-%m-%dT%H:%M:%S.%f')
    return iso_8601_dt.replace(tzinfo=timezone('UTC')).astimezone(tz_info)

def french_string_to_boolean(french_string: str) -> bool:

    french_string = french_string.upper()

    if french_string == 'OUI':
        boolean = True
    elif french_string == 'NON':
        boolean = False
    else:
        pass

    return boolean

dtypes = {'datasetid': 'string',
          'recordid': 'string',
          #'record_timestamp': 'object',
          'fields.name': 'string',
          'fields.stationcode': 'string',
          'fields.ebike': 'int64',
          'fields.mechanical': 'int64',
          'fields.coordonnees_geo': 'object',
          'fields.duedate': 'string',
          'fields.numbikesavailable': 'int64',
          'fields.numdocksavailable': 'int64',
          'fields.capacity': 'int64',
          'fields.is_renting': 'bool',
          'fields.is_installed': 'bool',
          'fields.nom_arrondissement_communes': 'string',
          'fields.is_returning': 'bool',
          'geometry.type': 'string',
          'geometry.coordinates': 'object',
          'geo_long': 'float',
          'geo_lat': 'float',
          }


def call_api(base_url: str, search_dict: dict) -> pd.DataFrame:
    r = requests.get(generate_q_url(base_url, search_dict))
    payload = json.loads(r.text)
    payload = payload['records']
    payload = pd.json_normalize(payload)

    bool_cols = ['fields.is_renting', 'fields.is_installed', 'fields.is_returning']

    for bool_col in bool_cols:
        payload[bool_col] = payload[bool_col].apply(lambda x: french_string_to_boolean(str(x)))

    payload[['geo_long', 'geo_lat']] = pd.DataFrame(payload['fields.coordonnees_geo'].tolist(),
                                                    index=payload.index)

    payload['fields.duedate'] = payload['fields.duedate'].apply(lambda x: dt.datetime.fromisoformat(x))
    payload['record_timestamp'] = payload['record_timestamp'].apply(lambda x: dt.datetime.fromisoformat(x.split('.')[0]+'+00:00'))

    #x.replace('Z', '+00:00')))

    #REFERENCE TO OLD TIMESTEP *** Call from postrgres
    old_payload = load_payload_to_df('2023-04-19_17.28.51.757980_.json')

    difference_df = (payload[['fields.numbikesavailable','fields.stationcode']]
                            .merge(old_payload[['fields.numbikesavailable','fields.stationcode']],
                                   left_on='fields.stationcode',
                                   right_on='fields.stationcode',
                                   suffixes=('_new', '_old')))

    payload['difference'] = difference_df['fields.numbikesavailable_new'] - difference_df['fields.numbikesavailable_old']
    #print(payload[['fields.numbikesavailable','fields.numbikesavailable','difference']])

    payload.astype(dtype=dtypes)
    return payload

def save_payload(payload):
    base=str(Path(__file__).parent.parent.absolute())
    now_str = (str(datetime.datetime.now()).replace( " ", "_" ).replace( ":", "." ))

    with open(
            base+f'\\static\\test_data\\{now_str}_.json', 'w') as file:
        file.write(str(payload.to_json()))

def load_payload_to_df(filename:str):
    base = str(Path(__file__).parent.parent.absolute())
    with open(
            base + f'\\static\\test_data\\{filename}', 'r') as file:
        payload = file.read()

    return pd.read_json(payload)

save_payload(call_api(BASE_URL,search_dict))

#filename="2023-04-19_15.30.09.772246_.json"
#loaded_df = load_payload_to_df(filename)
