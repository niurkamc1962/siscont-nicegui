from datetime import datetime, date
from decimal import Decimal
import json

def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)

def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False
