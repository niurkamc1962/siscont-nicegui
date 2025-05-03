from typing import List, Dict
# from db.database import DatabaseManager
from db.utils import serialize_value  # importa tu helper
import logging

from stores.store import app_state

# Funcion para obtener los datos de SCPTrabajadores segun el query necesario para el JSON
def get_trabajadores(db) -> List[Dict]:
    query = """
    SELECT 
        T.CPTrabConsecutivoID,
        T.CPTrabNombre,
        T.CPTrabPriApellido,
        T.CPTrabSegApellido,
        T.TrabSexo,
        T.CategId,
        T.CargId,
        T.TrabFechaAlta,
        T.TrabFechaBaja,
        T.TrabFormaCobro,
        T.TrabTmagnMN,
        T.TrabCorreo,
        T.TrabCPVacaciones,
        T.TipTrabId,
        C.CargDescripcion,
        TT.TipTrabDescripcion,
        R.ProvCod,
        R.MunicCod,
        R.TRepartosCodigo,
        R.TRepartosNombre,
        PD.SRHPersDireccionDir,
        PD.SRHPersDireccionOficial
    FROM SCPTrabajadores AS T
    LEFT JOIN SNOCARGOS AS C ON T.CargId = C.CargId
    LEFT JOIN SNOTIPOTRABAJADOR AS TT ON T.TipTrabId = TT.TipTrabId
    LEFT JOIN SRHPersonas AS P ON T.CPTrabConsecutivoID = P.SRHPersonasId
    LEFT JOIN SRHPersonasDireccion AS PD ON P.SRHPersonasId = PD.SRHPersonasId
    LEFT JOIN TEREPARTOS AS R ON PD.TRepartosCodigo = R.TRepartosCodigo
    WHERE (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                row_dict = {
                    col: serialize_value(val) for col, val in zip(columns, row)
                }
                result.append(row_dict)

            return result

    except Exception as e:
        logging.error(f"Error al obtener SCPTrabajadores: {e}")
        raise Exception(f"Error al obtener datos de SCPTrabajadores: {str(e)}")



# Prepara la relacion entre las tablas con SCPTrabajadores
def get_relaciones_trabajadores(db) -> List[Dict]:
    query = """
    SELECT 
        fk.table_name AS source_table,
        fk.column_name AS source_column,
        pk.table_name AS target_table,
        pk.column_name AS target_column
    FROM 
        information_schema.referential_constraints rc
    JOIN 
        information_schema.key_column_usage fk ON rc.constraint_name = fk.constraint_name
    JOIN 
        information_schema.key_column_usage pk ON rc.unique_constraint_name = pk.constraint_name
    WHERE 
        fk.table_name IN ('SCPTrabajadores', 'SNOCARGOS', 'SNOTIPOTRABAJADOR', 'SRHPersonas', 'SRHPersonasDireccion', 'TEREPARTOS')
        OR pk.table_name IN ('SCPTrabajadores', 'SNOCARGOS', 'SNOTIPOTRABAJADOR', 'SRHPersonas', 'SRHPersonasDireccion', 'TEREPARTOS')
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    'source_table': row[0],
                    'source_column': row[1],
                    'target_table': row[2],
                    'target_column': row[3],
                }
                for row in rows
            ]
    except Exception as e:
        logging.error(f"Error al obtener relaciones entre tablas: {e}")
        raise

def construir_tree_trabajadores(relaciones):
    tree = {}
    counter = 1  # para generar IDs únicos

    for rel in relaciones:
        src = rel["source_table"]
        tgt = rel["target_table"]
        src_col = rel["source_column"]
        tgt_col = rel["target_column"]

        if src not in tree:
            tree[src] = {
                "id": src,
                "description": f"Relaciones desde {src}",
                "children": {}
            }

        if tgt not in tree[src]["children"]:
            tree[src]["children"][tgt] = {
                "id": f"{src}_{tgt}",
                "description": f"Relaciones hacia {tgt}",
                "children": []
            }

        tree[src]["children"][tgt]["children"].append({
            "id": f"rel_{counter}",
            "description": f"{src_col} → {tgt}.{tgt_col}"
        })

        counter += 1

    # convertir a lista y formatear recursivamente
    return [
        {
            "id": src_node["id"],
            "description": src_node["description"],
            "children": list(tgt_dict.values())
        } for src_node in tree.values() for tgt_dict in [src_node["children"]]
    ]

