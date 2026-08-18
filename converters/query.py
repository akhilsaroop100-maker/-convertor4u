import re
from decimal import Decimal

from .engine import convert
from .models import Unit

NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
COMPONENT_RE = re.compile(rf"({NUMBER})\s*([^\d+.-]+?)(?=\s*{NUMBER}\s*[^\d]|$)", re.IGNORECASE)


class QueryError(ValueError):
    pass

def normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower().replace("_", " ").replace("-", " "))

def unit_terms(unit):
    terms = {unit.name, unit.plural, unit.symbol, unit.slug.replace("-", " ")}
    terms.update(alias.strip() for alias in unit.aliases.split(",") if alias.strip())
    return {normalize(term) for term in terms}

def _split_query(query):
    text = re.sub(r"\s+", " ", (query or "").strip())
    to_match = re.match(r"^(.+?)\s+to\s+(.+?)$", text, re.IGNORECASE)
    if to_match:
        return to_match.groups()
    in_matches = list(re.finditer(r"\s+in\s+", text, re.IGNORECASE))
    if in_matches:
        divider = in_matches[-1]
        return text[:divider.start()], text[divider.end():]
    raise QueryError("Try a query like ‘72 kg to lb’ or ‘5 ft 11 in to cm’.")


def _resolve(term, units):
    normalized = normalize(term)
    return [unit for unit in units if normalized in unit_terms(unit)]


def parse_conversion_query(query):
    source_text, target_text = _split_query(query)
    units = list(Unit.objects.filter(is_active=True, category__is_active=True).select_related("category"))
    targets = _resolve(target_text, units)
    if not targets:
        raise QueryError("The target unit was not found.")
    raw_components = COMPONENT_RE.findall(source_text)
    components = [(Decimal(amount), term.strip()) for amount, term in raw_components]
    consumed = " ".join(f"{amount} {term}" for amount, term in raw_components)
    compact = lambda text: re.sub(r"\s+", "", text.lower())
    if not components or compact(consumed) != compact(source_text):
        raise QueryError("Use a number before each unit, for example ‘5 ft 11 in to cm’.")
    resolved = []
    for amount, term in components:
        matches = _resolve(term, units)
        if not matches:
            raise QueryError(f"The unit ‘{term}’ was not found.")
        resolved.append((amount, matches))
    compatible = []
    for target in targets:
        choices = [[unit for unit in matches if unit.category_id == target.category_id] for _, matches in resolved]
        if all(choices):
            compatible.append((target, [choice[0] for choice in choices]))
    if not compatible:
        raise QueryError("Those units were not found in the same conversion category.")
    target, component_units = compatible[0]
    source = component_units[0]
    if len(components) > 1 and any(unit.mode != Unit.FACTOR for unit in component_units):
        raise QueryError("Compound queries currently support additive measurement units such as feet and inches.")
    amount = sum((convert(value, unit, source) for (value, _), unit in zip(components, component_units)), Decimal("0"))
    display = " ".join(f"{value:g} {unit.symbol}" for (value, _), unit in zip(components, component_units))
    return amount, source, target, display
