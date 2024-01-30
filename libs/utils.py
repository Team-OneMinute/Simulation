def format_decimal(value):
    """
    小数を小数点以下2位でカットする。
    """
    if isinstance(value, float):
        return round(value, 2)
    return value
