from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ConexionParams(BaseModel):
    host: str
    database: str
    password: str


class Relacion(BaseModel):
    tabla_padre: str
    columna_padre: str
    tabla_hija: str
    columna_hija: str


class Campo(BaseModel):
    nombre_campo: str
    tipo_campo: str
    obligatorio: bool
    nombre_campo_erp: str  # nombre del campo en el doctype
    tipo_campo_erp: str  # tipo de campo en el doctype


class TablaSQL(BaseModel):
    nombre_tabla: str  # nombre descriptivo de la tabla SQL
    nombre_tabla_sql: str  # Nombre real en la tabla SQL
    campos: List[Campo]
    nombre_doctype: str  # nombre del Doctype


class Payload(BaseModel):
    params: ConexionParams
    fields: List[Campo]
    

# Modelo para el endpoint de generar Doctype JSON
class GenerateDoctype(BaseModel):
    params: ConexionParams
    fields: List[Campo]
    module: Optional[str] = "Custom"
    is_child_table: Optional[bool] = False
    # custom_fields: Optional[List[Dict[str, Any]]] = None
