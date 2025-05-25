# Funciones relacionadas con NOMINA
import math
from typing import List, Dict, Any

from utils.jsons_utils import save_json_file
from utils.serialization import serialize_value  # importa tu helper
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Funcion para obtener los datos de SCPTrabajadores segun el query necesario para el JSON
def get_trabajadores(db) -> List[Dict]:
    doctype_name = "Employee"
    sqlserver_name = "SCPTRABAJADORES"
    module_name = "Setup"

    # Definimos un mapeo explícito de campos
    field_mapping = [
        # Campos del doctype principal (trabajador)
        ("identity_number", ("employee", "T.CPTrabConsecutivoID")),
        ("first_name", ("employee", "T.CPTrabNombre")),
        ("last_name", ("employee", "T.CPTrabPriApellido")),
        ("second_surname", ("employee", "T.CPTrabSegApellido")),
        ("gender", ("employee", "T.TrabSexo")),
        ("date_of_joining", ("employee", "T.TrabFechaAlta")),
        ("contract_end_date", ("employee", "T.TrabFechaBaja")),
        ("salary_mode", ("employee", "T.TrabFormaCobro")),
        ("banc_ac_no", ("employee", "T.TrabTmagnMN")),
        ("company_email", ("employee", "T.TrabCorreo")),
        ("accumulate_vacation", ("employee", "T.TrabCPVacaciones")),
        ("direccion", ("employee", "PD.SRHPersDireccionDir")),
        ("oficial", ("employee", "PD.SRHPersDireccionOficial")),
        # Campos de otros doctypes
        ("category_name", ("occupational_category", "C.CategODescripcion")),
        ("designation_name", ("designation", "CAR.CargDescripcion")),
        ("province_name", ("province", "R.ProvCod")),
        ("id", ("city", "R.MunicCod")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (_, sql_field) in field_mapping
    ]

    query = f"""
    SELECT
        {', '.join(select_clauses)}
    FROM SCPTrabajadores AS T
    LEFT JOIN SNOCARGOS AS CAR ON T.CargId = CAR.CargId
    LEFT JOIN SNOCATEGOCUP AS C ON T.CategId = C.CategId
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
                item = {}

                for col, val in zip(columns, row):
                    for alias, (doctype, _) in field_mapping:
                        if alias == col:
                            val = serialize_value(val)
                            if doctype == "employee":
                                # campo del doctype
                                item[alias] = val
                            else:
                                # Los campos que son link a otros doctype
                                if doctype not in item:
                                    item[doctype] = {}
                                item[doctype][alias] = val
                            break

                # result.append({"employee": employee_data})
                result.append(item)
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
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
    doctype_name = "Occupational Category"
    sqlserver_name = "SNOCATEGOCUP"
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

            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de las categorias ocupacionales: {e}")
        raise


# Para obtener los cargos de los trabajadores
def get_cargos_trabajadores(db):
    doctype_name = "Designation"
    sqlserver_name = "SNOCARGOS"
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los cargos de los trabajadores: {e}")
        raise


# Para obtener los tipos de trabajadores
def get_tipos_trabajadores(db):
    doctype_name = "Employment Type"
    sqlserver_name = "SNOCTIPOTRABAJADOR"
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de trabajadores: {e}")
        raise


# Para obtener las retenciones
def get_tipos_retenciones(db):
    doctype_name = "Withholding Type"
    sqlserver_name = "SCPCONRETPAGAR"
    module_name = "Cuba"
    query = """
        SELECT CPCRetDescripcion  as withholding_type_name, 
        CRetDeudaCon as debt_to, 
        c.ClcuDescripcion as account,
        CRetPPrioridad as priority,
        CRetPPenAlimenticia as child_support,
        CRetPConPlazos as by_installments 
        FROM SCPCONRETPAGAR s LEFT JOIN SCGCLASIFICADORDECUENTAS c ON s.ClcuIDCuenta = c.ClcuIDCuenta
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de retenciones: {e}")
        raise


# Para obtener loa pensionados
def get_pensionados(db):
    doctype_name = "Customer"
    sqlserver_name = "SNOMANTPENS"
    module_name = "Selling"
    query = """
        SELECT MantPensCiPens as NODEFINIDO, 
        (MantPensNombre + ' ' + MantPensPriApe + ' ' + MantPensSegApe ) as customer_name, 
        MantPensDir as customer_primary_address, 
        MantPensFormPag as NODEFINIDO,
        MantPensTMagn as NODEFINIDO
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los pensionados: {e}")
        raise


# Para obtener tasas de destajo
def get_tasas_destajos(db):
    doctype_name = "NODEFINIDO"
    sqlserver_name = "SNONOMENCLADORTASASDESTAJO"
    module_name = "NODEFINIDO"
    query = """
        SELECT TasaDDescripcion as item_name , 
        TasaDTasa as price_list_rate
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de las tasas de destajos: {e}")
        raise


# Para obtener colectivos
def get_colectivos(db):
    doctype_name = "Employee Group"
    sqlserver_name = "SNONOMENCLADORCOLECTIVOS"
    module_name = "Setup"
    query = """
        SELECT ColecId as colecId , ColecDescripcion as employee_group_name
        FROM SNONOMENCLADORCOLECTIVOS
        WHERE ColecDesactivado  != '' OR ColecDesactivado IS NOT NULL
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los colectivos: {e}")
        raise


# Para obtener departamentos
def get_departamentos(db):
    doctype_name = "Department"
    sqlserver_name = "SMGAREASUBAREA"
    module_name = "Setup"
    query = """
        SELECT 
            s.AreaDescrip as parent_department,
            s1.sareaDescrip as department_name
        FROM 
            SMGAREASUBAREA s
        LEFT JOIN 
            SMGAREASUBAREA1 s1 ON s.AreaCodigo = s1.AreaCodigo
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
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los departamentos: {e}")
        raise


# Para submayor de vacaciones
def get_submayor_vacaciones(db):
    doctype_name = "Employee Opening Vacation Subledger"
    sqlserver_name = "SNOSMVACACIONES"
    module_name = "Cuba"
    logging.info("Antes del query de vacaciones")
    query = """
        SELECT TOP 1000
            s.SMVacSaldoInicialI as initial_balance_in_amount,
            s.SMVacSaldoInicialD as initial_balance_in_days,        
            s.CPTrabConsecutivoID as employee, 
            s2.CPTrabExp as expediente_laboral
        FROM SNOSMVACACIONES s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID
    """
    logging.info("Despues del query y antes del try")
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            logging.info("Pase por rows")
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )

            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos del submayor de vacaciones: {e}")
        raise


# Para submayor de salarios no reclamados
def get_submayor_salarios_no_reclamados(db):
    doctype_name = "Opening of the Unclaimed Salary Subledger"
    sqlserver_name = "SNOSMREINTEGRONR"
    module_name = "Cuba"
    query = """
            select
                CPTrabConsecutivoID as employee,
                SMrnrImporte as amount,
                SMrnrFecha as reimbursement_date                
            from
                SNOSMREINTEGRONR s
            where
                SMrnrDebito = 0
                AND SMrnrIdenPaga IS NULL
    """
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            logging.info("Pase por rows")
            # serializando los campos para que no de error los decimales
            result = [
                {key: serialize_value(value) for key, value in zip(columns, row)}
                for row in rows
            ]
            output_path = save_json_file(
                doctype_name, result, module_name, sqlserver_name
            )

            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
            return result
    except Exception as e:
        logging.error(f"Error al obtener datos de los salarios no reclamados:" f" {e}")
        raise


# --- Función para generar un ÚNICO JSON con TODOS los datos paginados ---
def generate_full_vacaciones_json(db, page_size: int = 100) -> Dict[str, Any]:
    """
    Recopila todos los datos del submayor de vacaciones paginando y los guarda
    en un único archivo JSON.
    Retorna información sobre el archivo generado y el total de registros.
    """
    doctype_name = "Employee Opening Vacation Subledger"
    sqlserver_name = "SNOSMVACACIONES"
    module_name = "Cuba"

    logging.info("Contando total de registros para la exportación completa...")
    total_count_query = """
        SELECT COUNT(*)
        FROM SNOSMVACACIONES s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID;
    """

    base_query = """
        SELECT
            s.SMVacSaldoInicialI as initial_balance_in_amount,
            s.SMVacSaldoInicialD as initial_balance_in_days,
            s.CPTrabConsecutivoID as employee,
            s2.CPTrabExp as expediente_laboral
        FROM SNOSMVACACIONES s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID
        ORDER BY s.CPTrabConsecutivoID -- Crucial para una paginación consistente
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            # 1. Obtener el total de registros
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.info(f"Total de registros para exportar: {total_items}")

            if total_items == 0:
                logging.warning("No hay registros para exportar en SNOSMVACACIONES.")
                # Crear un archivo JSON vacío si no hay datos
                output_path = save_json_file(
                    doctype_name, [], module_name, sqlserver_name, suffix="_full"
                )
                return {
                    "total_items": 0,
                    "total_pages": 0,
                    "page_size": page_size,
                    "file_path": output_path,
                    "data_count": 0,
                    "message": "No hay registros para exportar.",
                }

            total_pages = math.ceil(total_items / page_size)
            logging.info(
                f"Se procesarán {total_pages} páginas de {page_size} registros cada una."
            )

            # 2. Iterar a través de todas las páginas para obtener los datos
            for page in range(total_pages):  # page starts from 0 to total_pages-1
                offset = page * page_size
                logging.info(
                    f"Obteniendo página {page + 1}/{total_pages} (offset: {offset}, limit: {page_size})..."
                )

                cursor.execute(base_query, offset, page_size)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            logging.info(f"Total de registros recopilados: {len(all_results)}")

        # 3. Guardar todos los datos en un único archivo JSON
        # La función save_json_file debe ser capaz de manejar un nombre de archivo sin el sufijo de página si lo deseas.
        # Ajustaré save_json_file en utils/jsons_utils.py para ser más flexible.
        output_path = save_json_file(
            doctype_name, all_results, module_name, sqlserver_name, suffix="_full"
        )

        logging.info(f"Todos los datos de vacaciones guardados en: {output_path}")

        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page_size": page_size,
            "file_path": output_path,  # Cambiado a 'file_path' para mayor claridad
            "data_count": len(all_results),
            "message": "Exportación completa de datos de vacaciones realizada exitosamente.",
        }

    except Exception as e:
        logging.error(f"Error en la exportación completa de vacaciones: {e}")
        raise Exception(f"Error en la exportación completa de vacaciones: " f"{str(e)}")
