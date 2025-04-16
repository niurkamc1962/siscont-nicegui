# db/db_manager.py
from os import getenv
from db.database import DatabaseManager

def create_db_manager(params: dict) -> DatabaseManager:
    return DatabaseManager(
        host=params['host'],
        password=params['password'],
        database=params['database'],
        port=params['port'],
        user=params['user'],
    )