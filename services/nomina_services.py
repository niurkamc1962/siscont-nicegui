# Llamadas a los endpoints de nomina
# Usando httpx que es  cliente moderno de Python para interactuar con APIs de forma asincrona 

from config.config import get_settings
import httpx
from stores.store import app_state

settings = get_settings()

# Llama al endpoiny trabajadores
async def fetch_trabajadores():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/trabajadores", json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()

# Llama al endpoint relaciones-trabajadores
async def fetch_relaciones_trabajadores():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/relaciones-trabajadores", json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()

# Llama al endpoint categorias-ocupacionales
async def fetch_categorias_ocupacionales():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/categorias-ocupacionales",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint cargos-trabajadores
async def fetch_cargos_trabajadores():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/cargos_trabajadores",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint tipos-trabajadores
async def fetch_tipos_trabajadores():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/tipos_trabajadores",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint tipos-retenciones
async def fetch_tipos_retenciones():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/tipos-retenciones",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint pensionados
async def fetch_pensionados():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/pensionados",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint tasas-destajos
async def fetch_tasas_destajos():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/tasas-destajos",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint colectivos
async def fetch_colectivos():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/colectivos",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()


# Llama al endpoint departamentos
async def fetch_departamentos():
    if app_state.db_params is None:
        raise ValueError("No DBParams encontrado. Asegurese que es esta autenticado en el sitio")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.API_BASE_URL}/nomina/departamentos",
                                     json=app_state.db_params.model_dump())
        response.raise_for_status()
        return response.json()