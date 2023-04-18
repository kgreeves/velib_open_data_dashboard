import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json, DictCursor
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
    def __init__(self, json: dict):
        self.nhits = json['nhits']
        self.parameters = json['parameters']
        self.records = json['records']
        self.facet_groups = json['facet_groups']

    def records_to_postgres(self):

        conn = connection_postgres()
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=DictCursor)

        for record in self.records:
            if record is not None:
                cursor.execute('INSERT INTO test_table ("testCol") VALUES (%s)',
                               [Json(record)]
                               )

        conn.commit()
        conn.close()

    def get_api_response_from_postgres(
            self,
    ) -> pd.DataFrame:
        conn = connection_postgres()
        conn.close()


response = VelibAPIResponse(test_data)

response.records_to_postgres()
