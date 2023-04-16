import requests
import json
import pandas as pd
from app.modules.querying import generate_q_url


def call_api(base_url: str, search_dict: dict) -> pd.DataFrame:
    r = requests.get(generate_q_url(base_url, search_dict))
    payload = json.loads(r.text)
    payload = payload['records']
    return pd.json_normalize(payload)
