from pydantic import BaseModel
from typing import List

class ConexionParams(BaseModel):
    host: str
    database: str
    password: str

class Campo(BaseModel):
    nombre_campo: str

class Payload(BaseModel):
    params: ConexionParams
    fields: List[Campo]

class GenerateDoctype(BaseModel):
    params: ConexionParams
