from decimal import Decimal, InvalidOperation, localcontext

class ConversionError(ValueError): pass

def as_decimal(value):
    try: return Decimal(str(value))
    except (InvalidOperation, ValueError): raise ConversionError("Enter a valid number.")

def convert(value, from_unit, to_unit):
    if from_unit.category_id != to_unit.category_id:
        raise ConversionError("Units must belong to the same category.")
    with localcontext() as ctx:
        ctx.prec = 32
        value = as_decimal(value)
        if from_unit.mode == "reciprocal":
            if value == 0: raise ConversionError("A reciprocal unit cannot convert zero.")
            base = from_unit.scale / value
        else:
            base = value * from_unit.scale + from_unit.offset
        if to_unit.mode == "reciprocal":
            if base == 0: raise ConversionError("A reciprocal result is undefined at zero.")
            return to_unit.scale / base
        return (base - to_unit.offset) / to_unit.scale

def format_decimal(value, places=10):
    value = Decimal(value)
    if value == 0: return "0"
    if abs(value) >= Decimal("1e12") or abs(value) < Decimal("1e-8"):
        return f"{value:.8E}".replace("E+", "e").replace("E", "e")
    text = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return text or "0"

def formula_text(source, target):
    if source.mode == "reciprocal" or target.mode == "reciprocal":
        return f"Convert through the category base ratio; {source.symbol} and {target.symbol} have an inverse relationship."
    if source.offset == 0 and target.offset == 0:
        factor = source.scale / target.scale
        return f"{target.symbol} = {source.symbol} × {format_decimal(factor, 12)}"
    return f"Convert {source.symbol} to the base scale, then apply the {target.symbol} scale and offset."
