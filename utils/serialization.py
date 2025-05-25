from datetime import datetime, date
from decimal import Decimal
import json
import logging

# Obtiene un logger con el nombre de este módulo
logger = logging.getLogger(__name__)

logging.warning("Entre en serialization")


def serialize_value(value):
    logging.warning(f"Serializando valoe: {value}, type: {type(value)}")
    if isinstance(value, (datetime, date)):
        # return value.isoformat()
        if value.year == 1753:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    logging.warning(f"Defaulting to str() for value: {value}, type: {type(value)}")
    return str(value)


def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False
