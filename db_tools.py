import os
import sys
from traceback import format_exc
import sqlalchemy as sqldb

from loguru import logger
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

PG_SERVER = 'postgresql'
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PASSWORD')
PG_HOST = os.getenv('POSTGRES_HOSTNAME')
PG_DB = os.getenv('DATABASE_NAME')

USER_TABLE = 'dd_users'
TIP_TABLE = 'transactions'

class Scribe:
    def __init__(self):
        self.engine_pattern = '{}://{}:{}@{}/{}'
        self.engine_name = self.engine_pattern.format(PG_SERVER,
                                                PG_USER, 
                                                PG_PW, 
                                                PG_HOST, 
                                                PG_DB)
        self.connect()

    def connect(self):
        self.engine = sqldb.create_engine(self.engine_name)
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()
        self.engine.dispose()

    def query(self, query):
        logger.debug('Executing query')
        result = None
        try:
            result = self.connection.execute(query)
        except Exception as e:
            logger.error(f'Error - {e}')
            logger.error(f'Traceback - {format_exc()}')
        logger.debug('Success')

    def select(self, query):
        logger.debug('Executing query')
        result = None
        try:
            result = self.connection.execute(query).fetchall()
        except Exception as e:
            logger.error(f'Error - {e}')
            logger.error(f'Traceback - {format_exc()}')
        logger.debug('Success')
        return result
        