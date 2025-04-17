# Ejemplo donde NiceGui es la app principal y FastAPI la subapp
# Muestra la interface web y los endpoints

from os import getenv
from fastapi import FastAPI
from nicegui import ui, app, Client
from views.main_view import main_view
from stores.store import AppState
from routes.api import router as api_router
import uvicorn

# Crear app FastAPI (backend)
fastapi_app = FastAPI()

# Incluir tus endpoints en FastAPI
fastapi_app.include_router(api_router, prefix="/api")


# Configurar estado global
app.state.store = AppState()

# Vista principal de NiceGUI (frontend)
@ui.page('/')
def index(client: Client):
    main_view(client)


# Ejecutar NiceGUI como la app principal
ui.run_with(
    fastapi_app,
    mount_path='/',  # Ruta base para NiceGUI
    storage_secret='tu_secreto_secreto',  # Necesario para sesiones
)

if __name__ == "__main__":
    port = int(getenv("PORT", 9802))
    uvicorn.run(
        "main:fastapi_app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
