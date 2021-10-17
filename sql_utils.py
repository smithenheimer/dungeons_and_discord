import psycopg2
from datetime import datetime
import sqlalchemy as sqldb
from dotenv import load_dotenv
import os

load_dotenv()

server = 'postgresql'
user = os.getenv('POSTGRES_USER')
pw = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOSTNAME')
database = os.getenv('DATABASE_NAME')

users = 'dd_users'
transactions = 'transactions'

class Scribe:
    def __init__(self):
        self.engine_pattern = '{}://{}:{}@{}/{}'
        print(self.engine_pattern)
        self.engine_name = self.engine_pattern.format(server,
                                                user, 
                                                pw, 
                                                host, 
                                                database)
        self.connect()

    def connect(self):
        self.engine = sqldb.create_engine(self.engine_name)
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()
        self.engine.dispose()

    def query(self, query):
        result = None
        try:
            result = self.connection.execute(query)
        except Exception as e:
            print(f'Error - {e}')
        return result
    