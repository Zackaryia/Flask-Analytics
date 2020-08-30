from datetime import date, datetime
from bson import ObjectId


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return obj.__str__