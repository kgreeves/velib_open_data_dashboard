import numpy
import requests
import json
import pandas as pd
from app.modules.querying import generate_q_url

dtypes = {'datasetid': 'string',
          'recordid': 'string',
          'record_timestamp': 'object',
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
          }

def call_api(base_url: str, search_dict: dict) -> pd.DataFrame:
    r = requests.get(generate_q_url(base_url, search_dict))
    payload = json.loads(r.text)
    payload = payload['records']
    payload = pd.json_normalize(payload)
    #payload.astype(dtype=dtypes)
    return payload
