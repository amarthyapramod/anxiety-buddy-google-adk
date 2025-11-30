from datetime import datetime

def timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")