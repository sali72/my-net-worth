from decimal import Decimal

MAX_INTEGER_PART = 10**10
MAX_DECIMAL_PART = 8

def check_value_precision(value: Decimal, field_name: str) -> Decimal:
    value = Decimal(str(value))
    if value == 0:
        raise ValueError(f"{field_name} cannot be zero")
    if value.as_tuple().exponent < -MAX_DECIMAL_PART:
        raise ValueError(
            f"{field_name} cannot have more than {MAX_DECIMAL_PART} decimal places"
        )
    if value >= MAX_INTEGER_PART:
        raise ValueError(
            f"{field_name} cannot have an integer part greater than {MAX_INTEGER_PART}"
        )
    return value