from pydantic import BaseModel
from typing import List, Optional

class ConexionParams(BaseModel):
    host: str
    database: str
    password: str

class FieldPayload(BaseModel):
    nombre_campo: str
    tipo_campo: str
    obligatorio: bool
    tipo_campo_erp: Optional[str] = None
    nombre_campo_erp: Optional[str] = None

class Payload(BaseModel):
    module: str
    is_child_table: Optional[bool] = False
    fields: List[FieldPayload]
