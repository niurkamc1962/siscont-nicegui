# stores/store.py
from pydantic import BaseModel

class DBParams(BaseModel):
    host: str
    user: str
    password: str
    database: str
    port: str

class AppState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.connected = False
        self.db_params: DBParams = None
        self.db_manager = None
        self.selected_module = None
        self.ip_server = None