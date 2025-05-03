# Llamadas a los endpoints de nomina
# Usando httpx que es  cliente moderno de Python para interactuar con APIs de forma asincrona 

from config import get_settings
import httpx
from stores.store import app_state

settings = get_settings()


async def fetch_trabajadores():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/trabajadores", json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()

async def fetch_relaciones_trabajadores():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/relaciones-trabajadores", json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()
