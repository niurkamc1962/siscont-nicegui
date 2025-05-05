from fastapi import APIRouter, HTTPException
from db.database import create_db_manager
from db.models import ConexionParams
# from db.db_nomina import get_trabajadores, get_relaciones_trabajadores, get_categorias_ocupacionales
from db import db_nomina as nomina
from fastapi.responses import JSONResponse
import json

router = APIRouter()


@router.post(
    "/trabajadores",
    summary="Lista todos los trabajadores",
    description="Muestra listado de los trabajadores segun campos seleccionados",
    tags=["Nómina"],
)
async def get_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = nomina.get_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPTrabajadores: {str(e)}",
        )


@router.post("/relaciones-trabajadores",
    summary="Muestra relacion de la tabla trabajadores con las demas",
    description="Muestra relacion entre las tablas con la de los trabajadores ",
    tags=["Nómina"])
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