

def safe_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except ValueError:
        return default