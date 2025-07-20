from sqlalchemy import func

def coalesced_sum(fields):
    """
    Returns a SQLAlchemy expression that sums the provided fields,
    wrapping each in func.coalesce(field, 0).
    """
    if not fields:
        return 0

    expr = func.coalesce(fields[0], 0)
    for field in fields[1:]:
        expr = expr + func.coalesce(field, 0)
    return expr
