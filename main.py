# Ejemplo donde NiceGui es la app principal y FastAPI la subapp
# Muestra la interface web y los endpoints

import os
from config.config import get_settings
from fastapi import FastAPI
from nicegui import ui, app, Client, storage
from views.main_view import main_view
from views.selected_module import selected_module
from stores.store import AppState, app_state
from routes.api import router as api_router
from routes.api_nomina import router as nomina_router
import uvicorn
from datetime import datetime
from db.database import create_db_manager
from db.models import ConexionParams

# Crear app FastAPI (backend)
fastapi_app = FastAPI(title='Siscont API')

# Incluir tus endpoints en FastAPI
fastapi_app.include_router(api_router, prefix="/api")
fastapi_app.include_router(nomina_router, prefix="/nomina")


# Configurar estado global para toda la aplicacion
app.state.store = AppState()

# Configurar el storage secret temprano
app.storage_secret = os.getenv("STORAGE_SECRET") or "siscont-erpnext"

# Función para restaurar el estado desde el almacenamiento
def init_app_state_from_storage():
    if app.storage.user.get('connected'):
        try:
            app_state.connected = True
            app_state.db_params = ConexionParams(**app.storage.user['db_params'])  # Reconstruir DBParams desde el dict guardado
            app_state.ip_server = app.storage.user.get('ip_server')
            app_state.last_activity = datetime.fromisoformat(app.storage.user.get('last_activity'))
            app_state.db_manager = create_db_manager(app_state.db_params)  # Reconstruir la conexión
        except Exception as e:
            print(f"Error restaurando estado: {e}")
            app_state.reset()


# Vista principal de NiceGUI (frontend)
@ui.page('/')
async def index(client: Client):
    # Llamar a la función para restaurar el estado desde el almacenamiento
    init_app_state_from_storage()
    await main_view(client)

@ui.page('/modulo/{module_name}')
async def module_page(client: Client, module_name: str):
    await selected_module(module_name)

# Ejecutar NiceGUI como la app principal
ui.run_with(
    fastapi_app,
    mount_path='/',  # Ruta base para NiceGUI
    storage_secret=app.storage_secret,  # Necesario para sesiones
)

if __name__ == "__main__":
    # port = int(getenv("PORT", 9802))
    settings = get_settings()
    uvicorn.run(
        "main:fastapi_app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
