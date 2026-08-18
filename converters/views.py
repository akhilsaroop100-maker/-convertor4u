from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .content import EXAMPLE_VALUES, pair_editorial
from .engine import ConversionError, convert, format_decimal, formula_text
from .currency import CurrencyServiceError, convert_currency, convert_currency_multi, historical_rates
from .forms import CorrectionReportForm
from .models import Category, FeaturedConversion, Unit
from .query import QueryError, parse_conversion_query
import time

STATIC_PAGES = {
    "unit-systems": {
        "eyebrow": "REFERENCE / 01", "title": "Common unit systems",
        "description": "A practical introduction to SI, US customary, and Imperial measurement systems.",
        "template": "converters/unit_systems.html",
    },
    "about": {
        "eyebrow": "CONVERTOR4U / ABOUT", "title": "Conversion without clutter",
        "description": "Why Convertor4U exists and how its calculations work.",
        "template": "converters/about.html",
    },
    "terms": {
        "eyebrow": "LEGAL / TERMS", "title": "Terms of use",
        "description": "Terms governing use of Convertor4U.",
        "template": "converters/terms.html",
    },
    "privacy": {
        "eyebrow": "LEGAL / PRIVACY", "title": "Privacy policy",
        "description": "How Convertor4U handles data and device-local preferences.",
        "template": "converters/privacy.html",
    },
    "accuracy": {
        "eyebrow": "EDITORIAL / STANDARDS", "title": "Accuracy and editorial standards",
        "description": "How Convertor4U defines units, calculates results, reviews content, and corrects errors.",
        "template": "converters/accuracy.html",
    },
}

def _unit_data(units):
    return [{"slug": u.slug, "name": u.name, "plural": u.plural, "symbol": u.symbol, "aliases": u.aliases, "scale": str(u.scale), "offset": str(u.offset), "mode": u.mode} for u in units]

def _popular_pairs(category, limit=8):
    featured = FeaturedConversion.objects.filter(category=category).select_related("from_unit", "to_unit")
    pairs = [{"source": item.from_unit, "target": item.to_unit, "url": f"/{category.slug}/{item.from_unit.slug}-to-{item.to_unit.slug}/", "reviewed": item.is_editorially_reviewed} for item in featured if item.from_unit.is_active and item.to_unit.is_active]
    if pairs:
        return pairs[:limit]
    units = list(category.units.filter(is_active=True)[:4])
    pairs = []
    for source in units:
        for target in units:
            if source.pk != target.pk:
                pairs.append({
                    "source": source, "target": target,
                    "url": f"/{category.slug}/{source.slug}-to-{target.slug}/",
                })
    return pairs[:limit]

def _site_url(request):
    return settings.SITE_URL or f"{request.scheme}://{request.get_host()}"

def _rate_limited(request, scope, limit=120):
    address = request.META.get("REMOTE_ADDR", "unknown")
    bucket = int(time.time() // 60)
    key = f"limit:{scope}:{address}:{bucket}"
    count = cache.get(key, 0)
    if count >= limit: return True
    cache.set(key, count + 1, 70)
    return False

def _seo(request, title, description):
    site_url = _site_url(request)
    return {
        "seo_title": title,
        "seo_description": description,
        "canonical_url": f"{site_url}{request.path}",
        "site_url": site_url,
    }

def home(request):
    categories = Category.objects.filter(is_active=True).prefetch_related("units")
    initial = categories.first()
    units = list(initial.units.filter(is_active=True)) if initial else []
    context = {"categories": categories, "initial": initial, "units": units, "unit_data": _unit_data(units), "converter_category_slug": initial.slug if initial else ""}
    featured = FeaturedConversion.objects.filter(is_editorially_reviewed=True, show_on_homepage=True, category__is_active=True, from_unit__is_active=True, to_unit__is_active=True).select_related("category", "from_unit", "to_unit").order_by("homepage_order", "category__order", "order")
    grouped = {}
    for item in featured:
        group = grouped.setdefault(item.category_id, {"category": item.category, "pairs": []})
        if len(group["pairs"]) < 4:
            group["pairs"].append({"source": item.from_unit, "target": item.to_unit, "url": f"/{item.category.slug}/{item.from_unit.slug}-to-{item.to_unit.slug}/", "reviewed": True})
    context["popular_groups"] = list(grouped.values())
    context.update(_seo(request, "Online Unit Converter – 124 Units in 17 Categories | Convertor4U", "Convert 124 units across length, mass, temperature, energy, power, fuel economy, data storage, currency, and more at Convertor4U.com. Instant results with formulas and tables."))
    return render(request, "converters/home.html", context)

def reference_page(request, page_slug):
    page = STATIC_PAGES.get(page_slug)
    if not page:
        raise Http404
    context = {"page": page, "categories": Category.objects.filter(is_active=True).prefetch_related("units")}
    context.update(_seo(request, f"{page['title']} | Convertor4U", page["description"]))
    return render(request, page["template"], context)

def site_map(request):
    context = {"categories": Category.objects.filter(is_active=True).prefetch_related("units")}
    context.update(_seo(request, "Converter Sitemap – All Units & Reference Pages | Convertor4U", "Browse every Convertor4U unit converter, measurement category, and unit-system reference page."))
    return render(request, "converters/site_map.html", context)

def contact(request):
    submitted = request.GET.get("submitted") == "1"
    form = CorrectionReportForm(request.POST or None, initial={"page_url": request.GET.get("page", "")})
    if request.method == "POST" and form.is_valid():
        if _rate_limited(request, "correction", 5):
            form.add_error(None, "Too many reports were submitted. Please wait a minute and try again.")
        else:
            form.save()
            return redirect("/contact/?submitted=1")
    context = {"form": form, "submitted": submitted}
    context.update(_seo(request, "Report a Correction or Contact Us | Convertor4U", "Report an inaccurate unit, formula, source, or page to the Convertor4U editorial team."))
    return render(request, "converters/contact.html", context)

def category(request, category_slug):
    cat = get_object_or_404(Category, slug=category_slug, is_active=True)
    units = list(cat.units.filter(is_active=True))
    context = {"category": cat, "initial": cat, "units": units, "unit_data": _unit_data(units), "converter_category_slug": cat.slug, "popular_pairs": _popular_pairs(cat, 12)}
    context.update(_seo(request, f"{cat.name} Converter – Convert {len(units)} Units Instantly | Convertor4U", f"Convert {cat.name.lower()} units instantly with exact calculations. Search {len(units)} units, swap values, copy results, and open detailed conversion tables."))
    return render(request, "converters/category.html", context)

def conversion(request, category_slug, pair_slug):
    cat = get_object_or_404(Category, slug=category_slug, is_active=True)
    if "-to-" not in pair_slug: raise Http404
    source_slug, target_slug = pair_slug.split("-to-", 1)
    source = get_object_or_404(Unit, category=cat, slug=source_slug, is_active=True)
    target = get_object_or_404(Unit, category=cat, slug=target_slug, is_active=True)
    samples = [Decimal(x) for x in ("1", "5", "10", "25", "50", "100")]
    example_value = EXAMPLE_VALUES.get(cat.slug, Decimal("10"))
    rate_date = None
    provider_status = "exact"
    if cat.slug == "currency":
        try:
            _, current_rate, rate_date, rate_stale = convert_currency(1, source, target)
            provider_status = "cached" if rate_stale else "live"
            rows = [(format_decimal(x), format_decimal(x * current_rate, 8)) for x in samples]
            one = format_decimal(current_rate, 12)
            example_result = format_decimal(example_value * current_rate, 8)
        except CurrencyServiceError:
            rows, one, example_result, rate_stale = [], "Temporarily unavailable", "unavailable", False
            provider_status = "unavailable"
    else:
        rows = [(format_decimal(x), format_decimal(convert(x, source, target), 8)) for x in samples]
        one = format_decimal(convert(1, source, target), 12)
        example_result = format_decimal(convert(example_value, source, target), 8)
    site_url = _site_url(request)
    canonical = f"{site_url}/{cat.slug}/{source.slug}-to-{target.slug}/"
    formula = f"{target.symbol} = {source.symbol} × current reference rate" if cat.slug == "currency" else formula_text(source, target)
    title = f"{source.plural.title()} to {target.plural.title()} Converter ({source.symbol} to {target.symbol}) | Convertor4U"
    description = f"Convert {source.plural} to {target.plural} instantly. 1 {source.symbol} = {one} {target.symbol}. Includes the exact formula, examples, and conversion table."
    related = [pair for pair in _popular_pairs(cat, 12) if not (pair["source"].pk == source.pk and pair["target"].pk == target.pk)][:8]
    review = FeaturedConversion.objects.filter(category=cat, from_unit=source, to_unit=target, is_editorially_reviewed=True).first()
    editorial = pair_editorial(cat, source, target, format_decimal(example_value), example_result)
    robots_meta = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" if review else "noindex,follow"
    return render(request, "converters/conversion.html", {"category": cat, "source": source, "target": target, "units": list(cat.units.filter(is_active=True)), "unit_data": _unit_data(cat.units.filter(is_active=True)), "rows": rows, "one": one, "formula": formula, "page_title": f"{source.plural} to {target.plural} Converter", "canonical": canonical, "canonical_url": canonical, "site_url": site_url, "rate_date": rate_date, "rate_stale": rate_stale if cat.slug == "currency" else False, "provider_status": provider_status, "seo_title": title, "seo_description": description, "related_pairs": related, "editorial": editorial, "review": review, "robots_meta": robots_meta, "ads_eligible": bool(review)})

def convert_api(request):
    if _rate_limited(request, "convert"):
        return JsonResponse({"error": "Too many requests. Please wait a moment."}, status=429)
    cat = get_object_or_404(Category, slug=request.GET.get("category"), is_active=True)
    source = get_object_or_404(Unit, category=cat, slug=request.GET.get("from"), is_active=True)
    target = get_object_or_404(Unit, category=cat, slug=request.GET.get("to"), is_active=True)
    try:
        if cat.slug == "currency":
            result, rate, rate_date, stale = convert_currency(request.GET.get("value", "0"), source, target)
            return JsonResponse({"result": format_decimal(result), "rate": format_decimal(rate, 12), "rate_date": rate_date, "rate_stale": stale, "provider_status": "cached" if stale else "live", "url": f"/{cat.slug}/{source.slug}-to-{target.slug}/"})
        result = convert(request.GET.get("value", "0"), source, target)
        return JsonResponse({"result": format_decimal(result), "rate": format_decimal(convert(1, source, target), 12), "provider_status": "exact", "url": f"/{cat.slug}/{source.slug}-to-{target.slug}/"})
    except (ConversionError, CurrencyServiceError) as exc:
        status = 503 if cat.slug == "currency" and isinstance(exc, CurrencyServiceError) else 400
        return JsonResponse({"error": str(exc), "provider_status": "unavailable" if status == 503 else "exact"}, status=status)

def multi_convert_api(request):
    if _rate_limited(request, "multi", 60):
        return JsonResponse({"error": "Too many requests. Please wait a moment."}, status=429)
    cat = get_object_or_404(Category, slug=request.GET.get("category"), is_active=True)
    source = get_object_or_404(Unit, category=cat, slug=request.GET.get("from"), is_active=True)
    targets = list(cat.units.filter(is_active=True).exclude(pk=source.pk)[:10])
    try:
        if cat.slug == "currency":
            converted, rate_date, stale = convert_currency_multi(request.GET.get("value", "0"), source, targets)
            rows = [{"slug": unit.slug, "name": unit.name, "symbol": unit.symbol, "result": format_decimal(value)} for unit, value in converted]
            return JsonResponse({"items": rows, "rate_date": rate_date, "rate_stale": stale, "provider_status": "cached" if stale else "live"})
        rows = [{"slug": unit.slug, "name": unit.name, "symbol": unit.symbol, "result": format_decimal(convert(request.GET.get("value", "0"), source, unit))} for unit in targets]
        return JsonResponse({"items": rows, "provider_status": "exact"})
    except (ConversionError, CurrencyServiceError) as exc:
        status = 503 if isinstance(exc, CurrencyServiceError) else 400
        return JsonResponse({"error": str(exc), "provider_status": "unavailable" if status == 503 else "exact"}, status=status)

def currency_history_api(request):
    if _rate_limited(request, "currency-history", 30):
        return JsonResponse({"error": "Too many requests. Please wait a moment."}, status=429)
    cat = get_object_or_404(Category, slug="currency", is_active=True)
    source = get_object_or_404(Unit, category=cat, slug=request.GET.get("from"), is_active=True)
    target = get_object_or_404(Unit, category=cat, slug=request.GET.get("to"), is_active=True)
    try:
        points = historical_rates(source.symbol, target.symbol, request.GET.get("days", 30))
        return JsonResponse({"points": points, "base": source.symbol, "quote": target.symbol, "provider_status": "live"})
    except (CurrencyServiceError, ValueError) as exc:
        return JsonResponse({"error": str(exc), "provider_status": "unavailable"}, status=503)

def units_api(request, category_slug):
    if _rate_limited(request, "units", 180):
        return JsonResponse({"error": "Too many requests. Please wait a moment."}, status=429)
    cat = get_object_or_404(Category, slug=category_slug, is_active=True)
    return JsonResponse({"units": _unit_data(cat.units.filter(is_active=True))})

def query_api(request):
    if _rate_limited(request, "query", 90):
        return JsonResponse({"error": "Too many requests. Please wait a moment."}, status=429)
    try:
        amount, source, target, input_display = parse_conversion_query(request.GET.get("q", ""))
        if source.category.slug == "currency":
            result, unit_rate, rate_date, stale = convert_currency(amount, source, target)
        else:
            result, unit_rate, rate_date, stale = convert(amount, source, target), convert(1, source, target), None, False
        return JsonResponse({"amount": format_decimal(amount, 12), "input": input_display, "result": format_decimal(result), "rate": format_decimal(unit_rate, 12), "rate_date": rate_date, "rate_stale": stale, "provider_status": "cached" if stale else ("live" if source.category.slug == "currency" else "exact"), "category": source.category.slug, "category_name": source.category.name, "from": source.slug, "from_name": source.name, "from_symbol": source.symbol, "to": target.slug, "to_name": target.name, "to_symbol": target.symbol, "url": f"/{source.category.slug}/{source.slug}-to-{target.slug}/?value={format_decimal(amount, 12)}"})
    except (QueryError, ConversionError, CurrencyServiceError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

def health(request):
    try:
        with connection.cursor() as cursor: cursor.execute("SELECT 1")
        response = JsonResponse({"status": "ok", "database": "ok"})
    except Exception:
        response = JsonResponse({"status": "degraded", "database": "unavailable"}, status=503)
    response["Cache-Control"] = "no-store"
    return response

def robots(request): return render(request, "robots.txt", {"site_url": _site_url(request)}, content_type="text/plain")

def page_not_found(request, exception):
    context = {"robots_meta": "noindex,nofollow"}
    context.update(_seo(request, "Page Not Found | Convertor4U", "The requested converter page could not be found."))
    return render(request, "404.html", context, status=404)

def server_error(request):
    context = {"robots_meta": "noindex,nofollow"}
    context.update(_seo(request, "Temporary Error | Convertor4U", "Convertor4U encountered a temporary problem."))
    return render(request, "500.html", context, status=500)

def maintenance(request):
    context = {"robots_meta": "noindex,nofollow", "seo_title": "Brief Maintenance | Convertor4U", "seo_description": "Convertor4U is briefly offline for maintenance.", "canonical_url": f"{_site_url(request)}/maintenance/"}
    response = render(request, "maintenance.html", context, status=503)
    response["Retry-After"] = "900"
    return response
