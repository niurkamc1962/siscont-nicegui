from typing import List, Dict

from utils.jsons_utils import save_json_file
from utils.serialization import serialize_value  # importa tu helper
import logging


# Funcion para obtener los datos de SCPTrabajadores segun el query necesario para el JSON
def get_trabajadores(db) -> List[Dict]:
    doctype_name = "employee"
    module_name = "Setup"

    # Definimos un mapeo explícito de campos
    field_mapping = [
        # Campos del doctype principal (trabajador)
        ('identity_number', ('employee', 'T.CPTrabConsecutivoID')),
        ('first_name', ('employee', 'T.CPTrabNombre')),
        ('last_name', ('employee', 'T.CPTrabPriApellido')),
        ('second_surname', ('employee', 'T.CPTrabSegApellido')),
        ('gender', ('employee', 'T.TrabSexo')),
        ('category_name', ('employee', 'T.CategId')),
        ('designation_name', ('employee', 'T.CargId')),
        ('date_of_joining', ('employee', 'T.TrabFechaAlta')),
        ('contract_end_date', ('employee', 'T.TrabFechaBaja')),
        ('salary_mode', ('employee', 'T.TrabFormaCobro')),
        ('banc_ac_no', ('employee', 'T.TrabTmagnMN')),
        ('company_email', ('employee', 'T.TrabCorreo')),
        ('accumulate_vacation', ('employee', 'T.TrabCPVacaciones')),
        ('direccion', ('employee', 'PD.SRHPersDireccionDir')),
        ('oficial', ('employee', 'PD.SRHPersDireccionOficial')),

        # Campos de otros doctypes
        ('province_name', ('province', 'R.ProvCod')),
        ('id', ('city', 'R.MunicCod')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (_, sql_field) in field_mapping
    ]

    query = f"""
    SELECT
        {', '.join(select_clauses)}
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
                employee_data = {}

                for col, val in zip(columns, row):
                    for alias, (doctype, _) in field_mapping:
                        if alias == col:
                            val = serialize_value(val)

                            if doctype == 'employee':
                                employee_data[alias] = val
                            else:
                                if doctype not in employee_data:
                                    employee_data[doctype] = {}
                                employee_data[doctype][alias] = val
                            break

                result.append({"employee": employee_data})

            output_path = save_json_file(doctype_name, result, module_name)
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")

            return result

    except Exception as e:
        logging.error(f"Error al obtener SCPTrabajadores: {e}")
        raise Exception(f"Error al obtener datos de SCPTrabajadores: {str(e)}")



# Prepara la relacion entre las tablas con SCPTrabajadores y las muestra en el frontend
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
                    "source_table": row[0],
                    "source_column": row[1],
                    "target_table": row[2],
                    "target_column": row[3],
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
                "children": {},
            }

        if tgt not in tree[src]["children"]:
            tree[src]["children"][tgt] = {
                "id": f"{src}_{tgt}",
                "description": f"Relaciones hacia {tgt}",
                "children": [],
            }

        tree[src]["children"][tgt]["children"].append(
            {"id": f"rel_{counter}", "description": f"{src_col} → {tgt}.{tgt_col}"}
        )

        counter += 1

    # convertir a lista y formatear recursivamente
    return [
        {
            "id": src_node["id"],
            "description": src_node["description"],
            "children": list(tgt_dict.values()),
        }
        for src_node in tree.values()
        for tgt_dict in [src_node["children"]]
    ]


# Para obtener las categorias ocupacionales y poniendo alias con el nombre del campo en el doctype
def get_categorias_ocupacionales(db):
    doctype_name = "occupacional_category"
    module_name = "Cuba"

    query = """
        SELECT CategODescripcion as category_name  
        FROM SNOCATEGOCUP 
        WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
    """

    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

            output_path = save_json_file(doctype_name, result, module_name )

            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de las categorias ocupacionales: {e}")
        raise


# Para obtener los cargos de los trabajadores
def get_cargos_trabajadores(db):
    doctype_name = "designation"
    module_name = "Setup"
    query = """
        SELECT CargDescripcion as designation_name
        FROM SNOCARGOS
        WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor: 
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(doctype_name, result, module_name)
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los cargos de los trabajadores: {e}")
        raise


# Para obtener los tipos de trabajadores
def get_tipos_trabajadores(db):
    doctype_name = "employment_type"
    module_name = "HR"
    query = """
        SELECT TipTrabDescripcion as employee_type_name
        FROM SNOTIPOTRABAJADOR s 
        WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(doctype_name, result, module_name)
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de trabajadores: {e}")
        raise


# Para obtener las retenciones
def get_tipos_retenciones(db):
    doctype_name = "withholding_type"
    module_name = "Cuba"
    query = """
        SELECT CPCRetDescripcion  as withholding_type_name, 
        CRetDeudaCon as debt_to, 
        ClcuIDCuenta as account,
        CRetPPrioridad as priority,
        CRetPPenAlimenticia as child_support,
        CRetPConPlazos as by_installments 
        FROM SCPCONRETPAGAR s
        WHERE CRetPDesactivado  = '' OR CRetPDesactivado IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(doctype_name, result, module_name)
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de retenciones: {e}")
        raise

# Para obtener loa pensionados
def get_pensionados(db):
    query = """
        SELECT MantPensCiPens, MantPensNombre, MantPensPriApe, MantPensSegApe, MantPensDir, MantPensFormPag, MantPensTMagn
        FROM SNOMANTPENS
        WHERE MantPensDesactivada  = '' OR MantPensDesactivada IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los pensionados: {e}")
        raise

# Para obtener tasas de destajo
def get_tasas_destajos(db):
    query = """
        SELECT TasaDDescripcion , TasaDTasa
        FROM SNONOMENCLADORTASASDESTAJO
        WHERE TasaDDescripcion  != '' OR TasaDDescripcion IS NOT NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de las tasas de destajos: {e}")
        raise
