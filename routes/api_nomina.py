from fastapi import APIRouter, HTTPException
from db.database import create_db_manager
from db.models import ConexionParams
from db.db_nomina import get_trabajadores, get_relaciones_trabajadores
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.post("/trabajadores", tags=["Nómina"])
async def get_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = get_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de SCPTrabajadores: {str(e)}")


@router.post("/relaciones-trabajadores", tags=["Nómina"])
async def get_relaciones_trabajadores_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = get_relaciones_trabajadores(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener relaciones entre tablas: {str(e)}")
