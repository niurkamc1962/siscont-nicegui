from os import getenv
from contextlib import contextmanager
import pyodbc

class DatabaseManager:
    def __init__(self, host: str, password: str, database: str, port: str, user: str):
        self.connection_params = {
            "host": host,
            "password": password,
            "database": database,
            "port": port,
            "user": user,
        }
        self._conn = None

    def connect(self):
        if self._conn is None:
            self._conn = self._create_connection()
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _create_connection(self):
        url = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.connection_params['host']};"
            f"PORT={self.connection_params['port']};"
            f"DATABASE={self.connection_params['database']};"
            f"UID={self.connection_params['user']};"
            f"PWD={self.connection_params['password']};"
            f"Timeout=0"
        )
        return pyodbc.connect(url)

    @contextmanager
    def cursor(self):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
