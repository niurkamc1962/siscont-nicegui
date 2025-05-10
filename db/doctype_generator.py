# db/doctype_generator.py

import json
from os import makedirs, path
from typing import List, Dict, Any


def map_sql_type_to_frappe(sql_type: str) -> str:
    sql_type = sql_type.lower()
    if "int" in sql_type:
        return "Int"
    elif "char" in sql_type or "text" in sql_type or "varchar" in sql_type:
        return "Data"
    elif "date" in sql_type:
        return "Date"
    elif "decimal" in sql_type or "numeric" in sql_type or "float" in sql_type:
        return "Float"
    elif "bit" in sql_type:
        return "Check"
    else:
        return "Data"


def _process_field(column: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "fieldname": column["column_name"].lower(),
        "fieldtype": map_sql_type_to_frappe(column["data_type"]),
        "label": column["column_name"].replace("_", " ").title(),
        "reqd": 0 if column["is_nullable"] == "YES" else 1,
        "in_list_view": 1,
        "columns": column["max_length"],
    }


def generate_frappe_doctype(
    table_name: str,
    table_structure: List[Dict],
    output_dir: str = "formatos_frappe"
) -> str:
    fields = [_process_field(col) for col in table_structure]

    doctype_json = {
        "doctype": "DocType",
        "name": table_name,
        "istable": 0,
        "editable_grid": 1,
        "autoname": "field: name",
        "fields": fields,
    }

    if not path.exists(output_dir):
        makedirs(output_dir)

    output_path = path.join(output_dir, f"{table_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(doctype_json, f, indent=4, ensure_ascii=False)

    return output_path