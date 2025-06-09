

def safe_int(value, default=0):
    """Convert ``value`` to ``int`` safely."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Convert ``value`` to ``float`` safely."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default