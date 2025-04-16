# Ejemplo donde FastAPI es la app principal y NiceGUI la subapp
# Muestra los endpoints y la interface web


from os import getenv
from fastapi import FastAPI
from nicegui import ui, app, Client
from views.main_view import main_view
from stores.store import AppState
from routes.api import router as api_router
import uvicorn

# 1. Crear app FastAPI
fastapi_app = FastAPI()
fastapi_app.include_router(api_router, prefix="/api")

# 2. Configurar estado global
app.state.store = AppState()

# 3. Vista principal de NiceGUI
@ui.page('/')
def index(client: Client):
    main_view(client)

# 4. Integración CORRECTA entre NiceGUI y FastAPI
# Opción 1: Montar NiceGUI dentro de FastAPI (recomendado)
fastapi_app.mount("/", app)

# Opción 2: Alternativa usando app.add_static_files (si necesitas servir archivos estáticos)
# app.add_static_files('/api', 'ruta/a/tus/archivos')

if __name__ == "__main__":
    port = int(getenv("PORT", 9801))
    
    # Ejecutar con Uvicorn directamente sobre la app FastAPI
    uvicorn.run(
        "main:fastapi_app",  # Import string para que funcione el reload
        host="0.0.0.0",
        port=port,
        reload=True
    )