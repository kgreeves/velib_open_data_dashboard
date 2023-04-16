import os
from os import getenv
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json, DictCursor
from app.modules.test_data import test_data

load_dotenv()

class VelibAPIResponse:
    def __init__(self, json: dict):
        self.nhits = json['nhits']
        self.parameters = json['parameters']
        self.records = json['records']
        self.facet_groups = json['facet_groups']

    def records_to_postgres(self):
        conn = psycopg2.connect(
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
        )

        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=DictCursor)

        for record in self.records:
            if record is not None:
                cursor.execute('INSERT INTO test_table ("testCol") VALUES (%s)',
                               [Json(record)]
                               )

        conn.commit()
        conn.close()


response = VelibAPIResponse(test_data)

print(response.records_to_postgres())
