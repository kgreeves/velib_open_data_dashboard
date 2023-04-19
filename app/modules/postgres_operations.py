import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json, DictCursor

from app.modules.api_operations import call_api
from app.modules.test_data import test_data

load_dotenv()


def connection_postgres():
    conn = psycopg2.connect(
        database=os.getenv('PG_DATABASE'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        host=os.getenv('PG_HOST'),
        port=os.getenv('PG_PORT'),
    )
    return conn


class VelibAPIResponse:
    def __init__(self, records: pd.DataFrame):
        self.response_df = records

    def records_to_postgres(self):

        conn = connection_postgres()
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=DictCursor)

        response_cols = ['fields.stationcode',
                         'fields.ebike',
                         'fields.mechanical',
                         'fields.numbikesavailable',
                         'fields.numdocksavailable',
                         'fields.is_renting',
                         'fields.is_installed',
                         'fields.is_returning',
                         'recordid',
                         'fields.duedate',
                         'record_timestamp',
                         ]

        postgres_cols = [col.split('.')[-1] for col in response_cols]

        for row in self.response_df[response_cols].values:

            cursor.execute(
                f'INSERT INTO bicycle_count ({", ".join(postgres_cols)}) VALUES ({(" %s," * len(postgres_cols))[:-1]})',
                tuple(row)
            )

        conn.commit()
        conn.close()

    def get_api_response_from_postgres(
            self,
    ) -> pd.DataFrame:
        conn = connection_postgres()
        conn.close()


def generate_station_detail_postgres(response_df: pd.DataFrame):

    conn = connection_postgres()
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=DictCursor)

    response_cols = ['fields.stationcode',
                  'fields.name',
                  'geo_long',
                  'geo_lat',
                  'fields.capacity',
                  'fields.nom_arrondissement_communes']

    postgres_cols = [col.split('.')[-1] for col in response_cols]

    for row in response_df.records_df[response_cols].values:
        cursor.execute(f'INSERT INTO station_detail ({", ".join(postgres_cols)}) VALUES ({(" %s,"*len(postgres_cols))[:-1]})',
                       tuple(row)
                       )

    conn.commit()
    conn.close()


def get_latest_bicycle_count() -> pd.DataFrame:
    conn = connection_postgres()
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=DictCursor)

    #Get all records with the most recent timestamp
    cursor.execute('''
        SELECT * FROM public.bicycle_count
        WHERE record_timestamp=(
            SELECT MAX (record_timestamp)
            FROM public.bicycle_count);
    ''')
    latest_df = cursor.fetchall()
    conn.commit()

    #Get Column Names
    cursor.execute("""
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'bicycle_count'
        """)
    table_cols = cursor.fetchall()
    table_cols = (pd.DataFrame(table_cols)
                  .iloc[:,3]
                  .to_list()
                  )

    ###CREATE DICTIONARY TO CONVERT FROM POSTGRES COLS TO API COLS.

    conn.commit()

    conn.close()

    return pd.DataFrame(latest_df, columns=table_cols)

if __name__ == "main":
    BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/?'

    search_dict = {
        'dataset': 'velib-disponibilite-en-temps-reel',
        'q': '',
        'rows': -1,
        'facet': []
    }

    current_payload = VelibAPIResponse(call_api(BASE_URL, search_dict))

    current_payload.records_to_postgres()

    #generate_station_detail_postgres(current_payload)