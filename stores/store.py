from pydantic import BaseModel
from datetime import datetime

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
        """Reinicia todos los estados a sus valores por defecto"""
        self.connected = False
        self.db_params: DBParams = None
        self.db_manager = None
        self.selected_module = None
        self.ip_server = None
        self.last_activity = None
    
    def update_activity(self):
        """Actualiza el timestamp de última actividad"""
        self.last_activity = datetime.now()
    
    def is_session_expired(self, timeout_minutes=30):
        """Verifica si la sesión ha expirado por inactividad"""
        if not self.last_activity:
            return True
        return (datetime.now() - self.last_activity).total_seconds() > timeout_minutes * 60

# Instancia global del estado
app_state = AppState()