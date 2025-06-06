# Endpoints de NOMINA
from fastapi import APIRouter, HTTPException, Query
from db.database import create_db_manager
from db.models import ConexionParams

# from db.db_nomina import get_trabajadores, get_relaciones_trabajadores, get_categorias_ocupacionales
from db import db_nomina as nomina
from fastapi.responses import JSONResponse

import logging

# Obtiene un logger con el nombre de este módulo
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/trabajadores",
    summary="Lista todos los trabajadores",
    description="Muestra listado de los trabajadores segun campos seleccionados",
    tags=["Nómina"],
)
async def get_trabajadores_endpoint(params: ConexionParams):
    logger.info("Endpoint trabajadores")
    try:
        with create_db_manager(params) as db:
            data = nomina.get_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPTrabajadores: {str(e)}",
        )


@router.post(
    "/relaciones-trabajadores",
    summary="Muestra relacion de la tabla trabajadores con las demas",
    description="Muestra relacion entre las tablas con la de los trabajadores ",
    tags=["Nómina"],
)
async def get_relaciones_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_relaciones_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relaciones entre tablas: {str(e)}",
        )


@router.post(
    "/categorias-ocupacionales",
    summary="Lista de categorías ocupacionales",
    description="Muestra las categorías ocupacionales activas",
    tags=["Nómina"],
)
async def get_categorias_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_categorias_ocupacionales(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de categorías: {str(e)}",
        )


@router.post(
    "/cargos-trabajadores",
    summary="Lista los cargos de los trabajadores",
    description="Muestra los cargos de los trabajadores",
    tags=["Nómina"],
)
async def get_cargos_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_cargos_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los cargos de los trabajadores: {str(e)}",
        )


@router.post(
    "/tipos-trabajadores",
    summary="Lista los tipos de trabajadores",
    description="Muestra los tipos de los trabajadores",
    tags=["Nómina"],
)
async def get_tipos_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_tipos_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los tipos de trabajadores: {str(e)}",
        )


@router.post(
    "/tipos-retenciones",
    summary="Lista los tipos de retenciones",
    description="Muestra los tipos de los retenciones",
    tags=["Nómina"],
)
async def get_tipos_retenciones_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_tipos_retenciones(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los tipos de retenciones {str(e)}",
        )


@router.post(
    "/pensionados",
    summary="Lista los pensionados",
    description="Muestra los pensionados",
    tags=["Nómina"],
)
async def get_pensionados_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_pensionados(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los pensionados {str(e)}",
        )


@router.post(
    "/tasas_destajos",
    summary="Lista las tasas de destajos",
    description="Muestra las tasas de destajos",
    tags=["Nómina"],
)
async def get_tasas_destajos_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_tasas_destajos(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de las tasas de destajos {str(e)}",
        )


@router.post(
    "/colectivos",
    summary="Lista los colectivos",
    description="Muestra los colectivos",
    tags=["Nómina"],
)
async def get_colectivos_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_colectivos(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los colectivos {str(e)}",
        )


@router.post(
    "/departamentos",
    summary="Lista los departamentos",
    description="Muestra los departamentos",
    tags=["Nómina"],
)
async def get_departamentos_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_departamentos(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los departamentos {str(e)}",
        )


@router.post(
    "/vacaciones",
    summary="Lista Submayor de Vacaciones",
    description="Muestra Submayor de Vacaciones",
    tags=["Nómina"],
)
async def get_submayor_vacaciones_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_submayor_vacaciones(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos del submayor de vacaciones"
            f" {str(e)}",
        )


@router.post(
    "/salarios",
    summary="Lista Submayor de salarios no reclamados",
    description="Muestra Submayor de Salarios No Reclamados",
    tags=["Nómina"],
)
async def get_ssubmayor_salarios_no_reclamados_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_submayor_salarios_no_reclamados(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos del submayor de salarios no "
            f"reclamados"
            f" {str(e)}",
        )
