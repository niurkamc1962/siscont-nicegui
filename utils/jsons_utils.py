# db/jsons_utils.py
# helpers
import os
import json

from config.config import get_output_dir

def save_json_file(doctype_name: str, data: list)-> str:
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{doctype_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({doctype_name: data}, f, indent=4, ensure_ascii=False)

    return output_path