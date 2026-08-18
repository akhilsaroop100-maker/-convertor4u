import json
from datetime import timedelta
from decimal import Decimal, InvalidOperation, localcontext
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.db import DatabaseError
from django.utils import timezone
from .models import CurrencyRate

API_URL = "https://api.frankfurter.dev/v2/rate/{base}/{quote}"
RATES_URL = "https://api.frankfurter.dev/v2/rates"
CACHE_SECONDS = 60 * 60 * 6


class CurrencyServiceError(RuntimeError):
    pass


def _request_json(url):
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "Convertor4U/1.0 (+https://convertor4u.com)"})
    with urlopen(request, timeout=6) as response:
        return json.loads(response.read().decode("utf-8"), parse_float=Decimal)


def latest_rate(base, quote):
    base, quote = base.upper(), quote.upper()
    if base == quote:
        return Decimal("1"), None, False
    cache_key = f"currency-rate:{base}:{quote}"
    cached = cache.get(cache_key)
    if cached:
        return Decimal(cached["rate"]), cached["date"], cached.get("stale", False)

    try:
        payload = _request_json(API_URL.format(base=base, quote=quote))
        rate = Decimal(payload["rate"])
        date = payload.get("date")
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError, InvalidOperation) as exc:
        try:
            saved = CurrencyRate.objects.filter(base=base, quote=quote).first()
        except DatabaseError:
            saved = None
        if saved:
            cached = {"rate": str(saved.rate), "date": saved.rate_date.isoformat() if saved.rate_date else None, "stale": True}
            cache.set(cache_key, cached, 60 * 15)
            return saved.rate, cached["date"], True
        raise CurrencyServiceError("Current exchange rates are temporarily unavailable.") from exc

    try:
        CurrencyRate.objects.update_or_create(base=base, quote=quote, defaults={"rate": rate, "rate_date": date})
    except DatabaseError:
        pass
    cache.set(cache_key, {"rate": str(rate), "date": date, "stale": False}, CACHE_SECONDS)
    return rate, date, False


def latest_rates(base, quotes):
    base = base.upper()
    quotes = list(dict.fromkeys(code.upper() for code in quotes if code.upper() != base))
    if not quotes:
        return {base: Decimal("1")}, None, False
    cache_key = f"currency-rates:{base}:{','.join(sorted(quotes))}"
    cached = cache.get(cache_key)
    if cached:
        return {code: Decimal(rate) for code, rate in cached["rates"].items()}, cached["date"], cached.get("stale", False)
    try:
        query = urlencode({"base": base, "quotes": ",".join(quotes)})
        payload = _request_json(f"{RATES_URL}?{query}")
        rates = {row["quote"].upper(): Decimal(row["rate"]) for row in payload}
        dates = [row.get("date") for row in payload if row.get("date")]
        if any(code not in rates for code in quotes):
            raise ValueError("Missing requested exchange rate")
        rate_date = max(dates) if dates else None
    except (HTTPError, URLError, TimeoutError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
        try:
            saved = {row.quote: row for row in CurrencyRate.objects.filter(base=base, quote__in=quotes)}
        except DatabaseError:
            saved = {}
        if any(code not in saved for code in quotes):
            raise CurrencyServiceError("Current exchange rates are temporarily unavailable.") from exc
        rates = {code: saved[code].rate for code in quotes}
        dates = [saved[code].rate_date.isoformat() for code in quotes if saved[code].rate_date]
        rate_date = max(dates) if dates else None
        cache.set(cache_key, {"rates": {code: str(rate) for code, rate in rates.items()}, "date": rate_date, "stale": True}, 60 * 15)
        return rates, rate_date, True
    try:
        for code, rate in rates.items():
            CurrencyRate.objects.update_or_create(base=base, quote=code, defaults={"rate": rate, "rate_date": rate_date})
    except DatabaseError:
        pass
    cache.set(cache_key, {"rates": {code: str(rate) for code, rate in rates.items()}, "date": rate_date, "stale": False}, CACHE_SECONDS)
    return rates, rate_date, False


def convert_currency_multi(value, source, targets):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CurrencyServiceError("Enter a valid amount.") from exc
    rates, date, stale = latest_rates(source.symbol, [target.symbol for target in targets])
    with localcontext() as context:
        context.prec = 32
        return [(target, amount if target.symbol.upper() == source.symbol.upper() else amount * rates[target.symbol.upper()]) for target in targets], date, stale


def historical_rates(base, quote, days=30):
    base, quote = base.upper(), quote.upper()
    days = max(7, min(int(days), 365))
    cache_key = f"currency-history:{base}:{quote}:{days}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    end = timezone.localdate()
    start = end - timedelta(days=days)
    query = urlencode({"base": base, "quotes": quote, "from": start.isoformat(), "to": end.isoformat()})
    try:
        payload = _request_json(f"{RATES_URL}?{query}")
        points = [{"date": row["date"], "rate": str(Decimal(row["rate"]))} for row in payload if row.get("quote", "").upper() == quote]
    except (HTTPError, URLError, TimeoutError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise CurrencyServiceError("Historical exchange-rate data is temporarily unavailable.") from exc
    if not points:
        raise CurrencyServiceError("No historical rates were returned for this period.")
    cache.set(cache_key, points, 60 * 60 * 24)
    return points


def convert_currency(value, source, target):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CurrencyServiceError("Enter a valid amount.") from exc
    rate, date, stale = latest_rate(source.symbol, target.symbol)
    with localcontext() as context:
        context.prec = 32
        return amount * rate, rate, date, stale
