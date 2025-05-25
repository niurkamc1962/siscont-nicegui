# db/jsons_utils.py
# helpers
import os
import json
from collections import OrderedDict
from typing import List, Dict, Any

from config.config import get_output_dir


def save_json_file(
    doctype_name: str,
    data: List[Dict[str, Any]],  # Changed 'list' to be more specific with type hinting
    module_name: str = None,
    sqlserver_name: str = None,
) -> str:
    """
    Guarda una lista de diccionarios como un archivo JSON.
    El nombre del archivo ahora incluye el doctype_name, sqlserver_name y un sufijo opcional
    para mayor claridad y evitar sobreescrituras.
    """
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

    # Clean doctype_name for filename, replacing spaces/slashes with underscores
    clean_doctype_name = (
        doctype_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    )

    # Construct the base filename from doctype_name and sqlserver_name for uniqueness
    file_base_name = clean_doctype_name
    if sqlserver_name:
        file_base_name = f"{sqlserver_name}"
        # file_base_name = f"{file_base_name}_{sqlserver_name}"

    # Add the suffix and the .json extension
    # output_filename = f"{file_base_name}{suffix}.json"
    output_filename = f"{file_base_name}.json"
    output_path = os.path.join(output_dir, output_filename)

    # Preparing the JSON content
    content = OrderedDict()
    # Uncomment these lines if you want to include them in the JSON output:
    # if sqlserver_name:
    #     content["sqlserver"] = sqlserver_name
    content["doctype"] = doctype_name
    # if module_name:
    #     content["module"] = module_name
    content["data"] = data

    # It's good practice to log what's happening
    print(
        f"Saving JSON to: {output_path}"
    )  # Using print here, but logging.info is better

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)

    return output_path
