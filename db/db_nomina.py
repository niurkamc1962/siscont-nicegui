# Funciones relacionadas con NOMINA
import math
from typing import List, Dict, Any
from utils.jsons_utils import save_json_file
from utils.serialization import serialize_value  # importa tu helper
import logging

logger = logging.getLogger(__name__)

from collections import OrderedDict  # se utiliza para el JSON


# --- Parámetros globales para la paginación ---
PAGINATION_THRESHOLD = (
    5000  # Número de registros a partir del cual se activa la paginación
)
DEFAULT_PAGE_SIZE = 1000  # Tamaño de cada página (chunk) al pagina


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

    # --- Consulta de conteo ---
    total_count_query = """
            SELECT COUNT(*)
            FROM SCPTrabajadores AS T
            LEFT JOIN SNOCARGOS AS CAR ON T.CargId = CAR.CargId
            LEFT JOIN SNOCATEGOCUP AS C ON T.CategId = C.CategId
            LEFT JOIN SNOTIPOTRABAJADOR AS TT ON T.TipTrabId = TT.TipTrabId
            LEFT JOIN SRHPersonas AS P ON T.CPTrabConsecutivoID = P.SRHPersonasId
            LEFT JOIN SRHPersonasDireccion AS PD ON P.SRHPersonasId = PD.SRHPersonasId
            LEFT JOIN TEREPARTOS AS R ON PD.TRepartosCodigo = R.TRepartosCodigo
            WHERE (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
        """

    # --- Consulta base para paginación (con ORDER BY) ---
    base_query = f"""
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
        ORDER BY T.CPTrabConsecutivoID 
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
        """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            # 1. Obtener el total de registros
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de trabajadores: {total_items}")

            if total_items == 0:
                logging.warning("No hay registros de trabajadores para exportar.")
                output_path = save_json_file(
                    doctype_name, [], module_name, sqlserver_name
                )
                return []  # Retorna una lista vacía si no hay datos

            if total_items > PAGINATION_THRESHOLD:
                # --- Paginación activada ---
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para trabajadores: {total_items} registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    logging.warning(
                        f"Obteniendo página {page_num + 1}/{total_pages} (offset: {offset}, limit: {DEFAULT_PAGE_SIZE})..."
                    )
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = []
                    for row in rows:
                        item = {}
                        for col, val in zip(columns, row):
                            for alias, (doctype, _) in field_mapping:
                                if alias == col:
                                    val = serialize_value(val)
                                    if doctype == "employee":
                                        item[alias] = val
                                    else:
                                        if doctype not in item:
                                            item[doctype] = {}
                                        item[doctype][alias] = val
                                    break
                        page_results.append(item)
                    all_results.extend(page_results)
            else:
                # --- Menos del umbral, obtener todo en una sola consulta ---
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} registros de trabajadores, "
                    f"obteniendo todo en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)  # offset 0, fetch all
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    item = {}
                    for col, val in zip(columns, row):
                        for alias, (doctype, _) in field_mapping:
                            if alias == col:
                                val = serialize_value(val)
                                if doctype == "employee":
                                    item[alias] = val
                                else:
                                    if doctype not in item:
                                        item[doctype] = {}
                                    item[doctype][alias] = val
                                break
                    all_results.append(item)

            logging.warning(
                f"Total de registros de trabajadores recopilados: {len(all_results)}"
            )
            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}_full.json guardado correctamente en {output_path}"
            )
            return all_results  # Retornar los datos recopilados

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
    logging.warning("Este es el logginf.warning para ver si funciona tambien")
    doctype_name = "Occupational Category"
    sqlserver_name = "SNOCATEGOCUP"
    module_name = "Cuba"

    total_count_query = """
            SELECT COUNT(*) FROM SNOCATEGOCUP
            WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
        """
    base_query = """
            SELECT 
                CategODescripcion as category_name
            FROM SNOCATEGOCUP
            WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
            ORDER BY CategId
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY;
        """

    all_results: List[Dict[str, Any]] = []
    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(
                f"Total de registros de categorías ocupacionales: {total_items}"
            )

            if total_items == 0:
                logging.warning("No hay categorías ocupacionales para exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para categorías: {total_items} registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} categorías, obteniendo todo en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}_full.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de las categorias ocupacionales: {e}")
        raise


# Para obtener los cargos de los trabajadores
def get_cargos_trabajadores(db):
    logging.warning("Entre en cargos trabajadores")
    doctype_name = "Designation"
    sqlserver_name = "SNOCARGOS"
    module_name = "Setup"

    total_count_query = """
        SELECT COUNT(*) FROM SNOCARGOS WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
    """

    base_query = """
        SELECT 
            CargDescripcion as designation_name
        FROM SNOCARGOS
        WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
        ORDER BY CargId
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(
                f"Total de registros de cargos de trabajadores:" f" {total_items}"
            )

            if total_items == 0:
                logging.warning("No hay cargos de trabajadores para exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para cargos trabajadores:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} cargos trabajadores, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los cargos de los trabajadores: {e}")
        raise


# Para obtener los tipos de trabajadores
def get_tipos_trabajadores(db):
    doctype_name = "Employment Type"
    sqlserver_name = "SNOCTIPOTRABAJADOR"
    module_name = "HR"

    total_count_query = """
            SELECT COUNT(*) FROM SNOTIPOTRABAJADOR WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
        """

    base_query = """
        SELECT 
            TipTrabDescripcion as employee_type_name
        FROM SNOTIPOTRABAJADOR s 
        WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
        ORDER BY TipTrabId
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(
                f"Total de registros de tipos de de trabajadores: {total_items}"
            )

            if total_items == 0:
                logging.warning("No hay tipos de de trabajadores para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para tipos de trabajadores:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} tipos de trabajadores, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de trabajadores: {e}")
        raise


# Para obtener las retenciones
def get_tipos_retenciones(db):
    doctype_name = "Withholding Type"
    sqlserver_name = "SCPCONRETPAGAR"
    module_name = "Cuba"

    total_count_query = """
        SELECT COUNT(*) FROM SCPCONRETPAGAR
        WHERE CRetPDesactivado  = '' OR CRetPDesactivado IS NULL
    """

    base_query = """
        SELECT 
        CPCRetDescripcion  as withholding_type_name, 
        CRetDeudaCon as debt_to, 
        c.ClcuDescripcion as account,
        CRetPPrioridad as priority,
        CRetPPenAlimenticia as child_support,
        CRetPConPlazos as by_installments 
        FROM SCPCONRETPAGAR s LEFT JOIN SCGCLASIFICADORDECUENTAS c ON s.ClcuIDCuenta = c.ClcuIDCuenta
        WHERE CRetPDesactivado  = '' OR CRetPDesactivado IS NULL
        ORDER BY CPCRetPCodigo
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(
                f"Total de registros de tipos de de retenciones: {total_items}"
            )

            if total_items == 0:
                logging.warning("No hay tipos de de retenciones para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para tipos de retenciones:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} tipos de retenciones, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los tipos de retenciones: {e}")
        raise


# Para obtener loa pensionados
def get_pensionados(db):
    doctype_name = "Customer"
    sqlserver_name = "SNOMANTPENS"
    module_name = "Selling"

    total_count_query = """
            SELECT COUNT(*) FROM SNOMANTPENS
            WHERE MantPensDesactivada  = '' OR MantPensDesactivada IS NULL
        """
    base_query = """
        SELECT MantPensCiPens as NODEFINIDO, 
        (MantPensNombre + ' ' + MantPensPriApe + ' ' + MantPensSegApe ) as customer_name, 
        MantPensDir as customer_primary_address, 
        MantPensFormPag as NODEFINIDO,
        MantPensTMagn as NODEFINIDO
        FROM SNOMANTPENS
        WHERE MantPensDesactivada  = '' OR MantPensDesactivada IS NULL
        ORDER BY MantPensCiPens
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de pensionados: {total_items}")

            if total_items == 0:
                logging.warning("No hay pensionados para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para pensionados:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} pensionados, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los pensionados: {e}")
        raise


# Para obtener tasas de destajo
def get_tasas_destajos(db):
    doctype_name = "NODEFINIDO"
    sqlserver_name = "SNONOMENCLADORTASASDESTAJO"
    module_name = "NODEFINIDO"

    total_count_query = """
                SELECT COUNT(*) FROM SNONOMENCLADORTASASDESTAJO
                WHERE TasaDDescripcion  != '' OR TasaDDescripcion IS NOT NULL
            """

    base_query = """
        SELECT 
        TasaDDescripcion as item_name , 
        TasaDTasa as price_list_rate
        FROM SNONOMENCLADORTASASDESTAJO
        WHERE TasaDDescripcion  != '' OR TasaDDescripcion IS NOT NULL
        ORDER BY TasaDId
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de tasas destajos: {total_items}")

            if total_items == 0:
                logging.warning("No hay tasas destajos para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para tasas destajos:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} tasas destajos, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de las tasas de destajos: {e}")
        raise


# Para obtener colectivos
def get_colectivos(db):
    logging.warning("Entre en get_colectivos")
    doctype_name = "Employee Group"
    sqlserver_name = "SNONOMENCLADORCOLECTIVOS"
    module_name = "Setup"

    total_count_query = """
                    SELECT COUNT(*) FROM SNONOMENCLADORCOLECTIVOS
                    WHERE ColecDesactivado  != '' OR ColecDesactivado IS NOT NULL
                """

    base_query = """
        SELECT 
            ColecId as colecId , ColecDescripcion as employee_group_name
        FROM SNONOMENCLADORCOLECTIVOS
        WHERE ColecDesactivado  != '' OR ColecDesactivado IS NOT NULL
        ORDER BY ColecId
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de colectivos: {total_items}")

            if total_items == 0:
                logging.warning("No hay colectivos para exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para colectivos:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} colectivos, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los colectivos: {e}")
        raise


# Para obtener departamentos
def get_departamentos(db):
    doctype_name = "Department"
    sqlserver_name = "SMGAREASUBAREA"
    module_name = "Setup"

    total_count_query = """
        SELECT COUNT(*) FROM SMGAREASUBAREA
    """

    base_query = """
        SELECT 
            s.AreaDescrip as parent_department,
            s1.sareaDescrip as department_name
        FROM 
            SMGAREASUBAREA s
        LEFT JOIN 
            SMGAREASUBAREA1 s1 ON s.AreaCodigo = s1.AreaCodigo
        ORDER BY s.AreaCodigo
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de departamentos: {total_items}")

            if total_items == 0:
                logging.warning("No hay departamentos para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para departamentos:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} departamentos, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los departamentos: {e}")
        raise


# Para submayor de vacaciones
def get_submayor_vacaciones(db):
    doctype_name = "Employee Opening Vacation Subledger"
    sqlserver_name = "SNOSMVACACIONES"
    module_name = "Cuba"

    total_count_query = """
        SELECT COUNT(*) FROM SNOSMVACACIONES
        WHERE SMVacDesactivado = '' OR SMVacDesactivado IS NOT  NULL
    """

    base_query = """
        SELECT 
            s.SMVacSaldoInicialI as initial_balance_in_amount,
            s.SMVacSaldoInicialD as initial_balance_in_days,        
            s.CPTrabConsecutivoID as employee, 
            s2.CPTrabExp as expediente_laboral
        FROM SNOSMVACACIONES s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID
        WHERE SMVacDesactivado = '' OR SMVacDesactivado IS NOT  NULL
        ORDER BY SMVacId
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros de Submayor Vacaciones: {total_items}")

            if total_items == 0:
                logging.warning("No hay Submayor Vacaciones para " "exportar.")
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para Submayor Vacaciones:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} Submayor Vacaciones, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos del submayor de vacaciones: {e}")
        raise


# Para submayor de salarios no reclamados
def get_submayor_salarios_no_reclamados(db):
    doctype_name = "Opening of the Unclaimed Salary Subledger"
    sqlserver_name = "SNOSMREINTEGRONR"
    module_name = "Cuba"

    total_count_query = """
            SELECT COUNT(*) FROM SNOSMREINTEGRONR
            WHERE SMrnrDebito = 0 AND SMrnrIdenPaga IS NULL
        """

    base_query = """
            SELECT
                CPTrabConsecutivoID as employee,
                SMrnrImporte as amount,
                SMrnrFecha as reimbursement_date                
            FROM SNOSMREINTEGRONR s
            WHERE SMrnrDebito = 0 AND SMrnrIdenPaga IS NULL
            ORDER BY SMrnrIdentificador
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY;
    """

    all_results: List[Dict[str, Any]] = []

    try:
        with db.cursor() as cursor:
            cursor.execute(total_count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(
                f"Total de registros de Submayor salarios no reclamados: {total_items}"
            )

            if total_items == 0:
                logging.warning(
                    "No hay Submayor salarios no reclamados para " "exportar."
                )
                # output_path = save_json_file(
                #     doctype_name, [], module_name, sqlserver_name, suffix="_full"
                # )
                return []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Activando paginación para Submayor salarios no reclamados:"
                    f" {total_items} "
                    f"registros, "
                    f"en {total_pages} páginas de {DEFAULT_PAGE_SIZE}."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    cursor.execute(base_query, offset, DEFAULT_PAGE_SIZE)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value)
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                logging.warning(
                    f"Menos de {PAGINATION_THRESHOLD} Submayor salarios no reclamados, "
                    f"obteniendo todo "
                    f"en una sola consulta."
                )
                cursor.execute(base_query, 0, total_items)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                page_results = [
                    {key: serialize_value(value) for key, value in zip(columns, row)}
                    for row in rows
                ]
                all_results.extend(page_results)

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(
                f"{doctype_name}.json guardado correctamente en {output_path}"
            )
            return all_results
    except Exception as e:
        logging.error(f"Error al obtener datos de los salarios no reclamados:" f" {e}")
        raise
