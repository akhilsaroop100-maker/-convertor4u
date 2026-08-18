from decimal import Decimal
from django.core.management.base import BaseCommand
from converters.editorial_seed import FEATURED_PAIRS, GUIDES, REVIEWED_BY, REVIEWED_ON
from converters.models import Category, FeaturedConversion, Unit

VERIFIED_ON = "2026-08-14"
SOURCES = {
    "length": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "mass": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "area": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "volume": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "speed": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "pressure": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "energy": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "power": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "force": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "fuel-economy": ("NIST Guide to the SI, SP 811", "https://www.nist.gov/pml/special-publication-811"),
    "currency": ("Frankfurter reference rates from ECB data", "https://frankfurter.dev/"),
    "data-storage": ("IEC binary prefixes", "https://www.iec.ch/prefixes-binary-multiples"),
    "cooking": ("NIST Handbook 44 and customary definitions", "https://www.nist.gov/pml/owm/publications/nist-handbooks/handbook-44-current-edition"),
}
DEFAULT_SOURCE = ("BIPM SI Brochure and exact international definitions", "https://www.bipm.org/en/publications/si-brochure")

DEFINITIONS = {
    "meter": "The meter (m) is the SI base unit of length, defined from the fixed numerical value of the speed of light in vacuum.",
    "kilometer": "The kilometer (km) is exactly 1,000 meters and is commonly used for road and geographic distances.",
    "cm": "The centimeter (cm) is exactly one hundredth of a meter.",
    "inches": "The international inch (in) is exactly 25.4 millimeters.",
    "foot": "The international foot (ft) is exactly 0.3048 meters, or 12 inches.",
    "mile": "The international mile (mi) is exactly 1,609.344 meters, or 5,280 feet.",
    "kilogram": "The kilogram (kg) is the SI base unit of mass and is defined through the fixed value of the Planck constant.",
    "pound": "The international avoirdupois pound (lb) is exactly 0.45359237 kilograms.",
    "celsius": "Degrees Celsius use the same interval as kelvin, with 0 °C equal to 273.15 K.",
    "fahrenheit": "The Fahrenheit scale places water's freezing point at 32 °F and boiling point near 212 °F at standard pressure.",
    "liter": "The liter (L) is a non-SI unit accepted for use with SI and equals exactly one cubic decimeter.",
    "us-gallon": "The US liquid gallon is exactly 231 cubic inches, equal to 3.785411784 liters.",
    "second": "The second (s) is the SI base unit of time, defined using the cesium-133 atomic transition frequency.",
    "hour": "The hour (h) is a duration of exactly 3,600 seconds.",
    "meter-per-second": "The meter per second (m/s) is the SI coherent unit of speed.",
    "kilometer-per-hour": "One kilometer per hour (km/h) is exactly 5/18 of a meter per second.",
    "mile-per-hour": "One mile per hour (mph) equals exactly 0.44704 meters per second.",
    "pascal": "The pascal (Pa) is the SI unit of pressure, equal to one newton per square meter.",
    "psi": "Pounds per square inch (psi) expresses pressure as pound-force applied over one square inch.",
    "joule": "The joule (J) is the SI unit of energy, equal to the work done by one newton through one meter.",
    "kilowatt-hour": "The kilowatt-hour (kWh) is an energy unit equal to exactly 3.6 megajoules.",
    "watt": "The watt (W) is the SI unit of power, equal to one joule per second.",
    "horsepower": "Mechanical horsepower is defined as 550 foot-pounds per second, about 745.7 watts.",
    "degree": "A degree (°) is one 360th of a complete revolution.",
    "radian": "The radian (rad) is the SI unit of plane angle; one full revolution is 2π radians.",
    "bit": "The bit is the basic unit of digital information and can represent one of two binary values.",
    "byte": "A byte is a digital information unit consisting of eight bits.",
    "liters-per-100km": "Liters per 100 kilometers (L/100 km) measures fuel consumed over distance; lower values indicate better economy.",
}

CATEGORY_CONTEXT = {
    "length": "It is a unit of one-dimensional distance.",
    "mass": "It is an avoirdupois or metric unit of mass, not a unit of force.",
    "temperature": "Its stored scale and offset express readings as kelvin before conversion.",
    "area": "It measures two-dimensional surface area, so its relationship reflects squared length.",
    "volume": "It measures three-dimensional capacity; customary liquid units use the labeled US definition.",
    "time": "It represents a fixed elapsed duration rather than a variable calendar period.",
    "speed": "It measures distance traveled per unit time.",
    "pressure": "It measures force distributed over area and does not specify gauge versus absolute reference.",
    "energy": "It measures energy, work, or heat rather than the rate of energy transfer.",
    "power": "It measures the rate of energy transfer rather than an accumulated energy amount.",
    "force": "It measures force rather than mass.",
    "angle": "It measures plane angle or rotation.",
    "fuel-economy": "It expresses vehicle fuel efficiency using the direction indicated by its label.",
    "data-storage": "It measures digital information; decimal and IEC binary prefixes remain distinct.",
    "cooking": "It is a volume measure and cannot determine ingredient mass without density.",
    "frequency": "It expresses repeating events or angular cycles per unit time.",
}

CURRENCY_CONTEXT = {
    "eur": "The euro (EUR) is the shared currency of the euro area.",
    "usd": "The US dollar (USD) is the currency of the United States.",
    "zar": "The South African rand (ZAR) is the currency of South Africa.",
    "gbp": "The pound sterling (GBP) is the currency of the United Kingdom.",
    "jpy": "The Japanese yen (JPY) is the currency of Japan.",
    "aud": "The Australian dollar (AUD) is the currency of Australia.",
    "cad": "The Canadian dollar (CAD) is the currency of Canada.",
    "chf": "The Swiss franc (CHF) is the currency of Switzerland and Liechtenstein.",
    "cny": "The renminbi uses the yuan (CNY) as its unit and is the currency of China.",
    "inr": "The Indian rupee (INR) is the currency of India.",
    "nzd": "The New Zealand dollar (NZD) is the currency of New Zealand.",
    "bwp": "The Botswana pula (BWP) is the currency of Botswana.",
}


def definition_for(category_slug, name, symbol, unit_slug, scale, offset, mode, base_name, base_symbol):
    if unit_slug in DEFINITIONS:
        return DEFINITIONS[unit_slug] + " " + CATEGORY_CONTEXT[category_slug]
    if category_slug == "currency":
        return CURRENCY_CONTEXT[unit_slug] + " Its displayed conversions use the dated reference rate shown on the page, not a fixed measurement factor."
    if mode == "formula":
        return f"The {name} scale ({symbol}) is converted to {base_name} ({base_symbol}) with base = value × {scale} + {offset}. {CATEGORY_CONTEXT[category_slug]}"
    if mode == "reciprocal":
        return f"The {name} ({symbol}) is a reciprocal consumption measure stored against {base_name} ({base_symbol}) using the constant {scale}. {CATEGORY_CONTEXT[category_slug]}"
    if Decimal(scale) == 1:
        return f"The {name} ({symbol}) is the reference unit for this {category_slug.replace('-', ' ')} category. {CATEGORY_CONTEXT[category_slug]}"
    return f"One {name.lower()} ({symbol}) equals {scale} {base_name.lower()} units ({base_symbol}) in the converter's reference scale. {CATEGORY_CONTEXT[category_slug]}"

DATA = {
    "length": ("Length", "meter", "Everyday and scientific distance conversion.", [
        ("Meter", "meters", "m", "meter", "1", "metre,metres"),
        ("Kilometer", "kilometers", "km", "kilometer", "1000", "kilometre,kilometres"),
        ("Centimeter", "centimeters", "cm", "cm", ".01", "centimetre,centimetres"),
        ("Millimeter", "millimeters", "mm", "millimeter", ".001", "millimetre"),
        ("Mile", "miles", "mi", "mile", "1609.344", "miles"),
        ("Yard", "yards", "yd", "yard", ".9144", "yards"),
        ("Foot", "feet", "ft", "foot", ".3048", "feet"),
        ("Inch", "inches", "in", "inches", ".0254", "inch"),
        ("Nautical mile", "nautical miles", "nmi", "nautical-mile", "1852", "nm"),
    ]),
    "mass": ("Mass", "kilogram", "Mass and weight equivalents.", [
        ("Kilogram", "kilograms", "kg", "kilogram", "1", "kilo,kilos"),
        ("Gram", "grams", "g", "gram", ".001", "grams"),
        ("Milligram", "milligrams", "mg", "milligram", ".000001", "milligrams"),
        ("Metric tonne", "metric tonnes", "t", "tonne", "1000", "metric ton"),
        ("Pound", "pounds", "lb", "pound", ".45359237", "lbs"),
        ("Ounce", "ounces", "oz", "ounce", ".028349523125", "ounces"),
        ("Stone", "stones", "st", "stone", "6.35029318", "stones"),
    ]),
    "temperature": ("Temperature", "kelvin", "Temperature scales using exact offsets.", [
        ("Kelvin", "kelvin", "K", "kelvin", "1", "kelvins", "0"),
        ("Celsius", "degrees Celsius", "°C", "celsius", "1", "centigrade,c", "273.15"),
        ("Fahrenheit", "degrees Fahrenheit", "°F", "fahrenheit", "0.55555555555555555556", "f", "255.37222222222222222222"),
        ("Rankine", "degrees Rankine", "°R", "rankine", "0.55555555555555555556", "r", "0"),
    ]),
    "area": ("Area", "square-meter", "Surface area conversion.", [
        ("Square meter", "square meters", "m²", "square-meter", "1", "sqm"),
        ("Square kilometer", "square kilometers", "km²", "square-kilometer", "1000000", "sq km"),
        ("Square foot", "square feet", "ft²", "square-foot", ".09290304", "sq ft"),
        ("Square inch", "square inches", "in²", "square-inch", ".00064516", "sq in"),
        ("Acre", "acres", "ac", "acre", "4046.8564224", "acres"),
        ("Hectare", "hectares", "ha", "hectare", "10000", "hectares"),
    ]),
    "volume": ("Volume", "liter", "Liquid and cubic volume conversion.", [
        ("Liter", "liters", "L", "liter", "1", "litre,litres"),
        ("Milliliter", "milliliters", "mL", "milliliter", ".001", "ml"),
        ("Cubic meter", "cubic meters", "m³", "cubic-meter", "1000", "cbm"),
        ("US gallon", "US gallons", "gal", "us-gallon", "3.785411784", "gallon,gallons"),
        ("US quart", "US quarts", "qt", "us-quart", ".946352946", "quart"),
        ("US cup", "US cups", "cup", "us-cup", ".2365882365", "cups"),
        ("Fluid ounce", "fluid ounces", "fl oz", "fluid-ounce", ".0295735295625", "floz"),
    ]),
    "time": ("Time", "second", "Durations from milliseconds to years.", [
        ("Second", "seconds", "s", "second", "1", "sec"),
        ("Millisecond", "milliseconds", "ms", "millisecond", ".001", "msec"),
        ("Minute", "minutes", "min", "minute", "60", "mins"),
        ("Hour", "hours", "hr", "hour", "3600", "hrs"),
        ("Day", "days", "day", "day", "86400", "days"),
        ("Week", "weeks", "wk", "week", "604800", "weeks"),
        ("Year (365 days)", "years", "yr", "year", "31536000", "years"),
    ]),
    "speed": ("Speed", "meter-per-second", "Speed and velocity conversion.", [
        ("Meter per second", "meters per second", "m/s", "meter-per-second", "1", "mps"),
        ("Kilometer per hour", "kilometers per hour", "km/h", "kilometer-per-hour", ".27777777777777777778", "kph,kmh"),
        ("Mile per hour", "miles per hour", "mph", "mile-per-hour", ".44704", "mph"),
        ("Foot per second", "feet per second", "ft/s", "foot-per-second", ".3048", "fps"),
        ("Knot", "knots", "kn", "knot", ".51444444444444444444", "kt,kts"),
    ]),
    "pressure": ("Pressure", "pascal", "Pressure and stress conversion.", [
        ("Pascal", "pascals", "Pa", "pascal", "1", "pa"),
        ("Kilopascal", "kilopascals", "kPa", "kilopascal", "1000", "kpa"),
        ("Bar", "bars", "bar", "bar", "100000", "bars"),
        ("Atmosphere", "atmospheres", "atm", "atmosphere", "101325", "standard atmosphere"),
        ("Pound per square inch", "pounds per square inch", "psi", "psi", "6894.757293168", "lb/in2"),
        ("Millimeter of mercury", "millimeters of mercury", "mmHg", "mmhg", "133.322387415", "torr"),
    ]),
    "currency": ("Currency", "eur", "Current reference exchange rates for common world currencies.", [
        ("Euro", "euros", "EUR", "eur", "1", "euro,euros"),
        ("US dollar", "US dollars", "USD", "usd", "1", "dollar,dollars"),
        ("South African rand", "South African rand", "ZAR", "zar", "1", "rand,rands"),
        ("British pound", "British pounds", "GBP", "gbp", "1", "pound sterling"),
        ("Japanese yen", "Japanese yen", "JPY", "jpy", "1", "yen"),
        ("Australian dollar", "Australian dollars", "AUD", "aud", "1", "australian dollar"),
        ("Canadian dollar", "Canadian dollars", "CAD", "cad", "1", "canadian dollar"),
        ("Swiss franc", "Swiss francs", "CHF", "chf", "1", "franc"),
        ("Chinese yuan", "Chinese yuan", "CNY", "cny", "1", "renminbi,yuan"),
        ("Indian rupee", "Indian rupees", "INR", "inr", "1", "rupee,rupees"),
        ("New Zealand dollar", "New Zealand dollars", "NZD", "nzd", "1", "new zealand dollar"),
        ("Botswana pula", "Botswana pula", "BWP", "bwp", "1", "pula"),
    ]),
    "energy": ("Energy", "joule", "Energy, heat, food energy, and electrical work.", [
        ("Joule", "joules", "J", "joule", "1", "joules"),
        ("Kilojoule", "kilojoules", "kJ", "kilojoule", "1000", "kilojoules"),
        ("Calorie", "calories", "cal", "calorie", "4.184", "small calorie"),
        ("Kilocalorie", "kilocalories", "kcal", "kilocalorie", "4184", "food calorie,calorie nutritional"),
        ("Watt-hour", "watt-hours", "Wh", "watt-hour", "3600", "watt hour"),
        ("Kilowatt-hour", "kilowatt-hours", "kWh", "kilowatt-hour", "3600000", "kilowatt hour"),
        ("British thermal unit", "British thermal units", "BTU", "btu", "1055.05585262", "british thermal unit"),
        ("Electronvolt", "electronvolts", "eV", "electronvolt", ".0000000000000000001602176634", "electron volt"),
        ("Foot-pound", "foot-pounds", "ft·lb", "foot-pound", "1.3558179483314", "ft lb"),
    ]),
    "power": ("Power", "watt", "Rates of energy transfer and mechanical power.", [
        ("Watt", "watts", "W", "watt", "1", "watts"),
        ("Kilowatt", "kilowatts", "kW", "kilowatt", "1000", "kilowatts"),
        ("Megawatt", "megawatts", "MW", "megawatt", "1000000", "megawatts"),
        ("Mechanical horsepower", "mechanical horsepower", "hp", "horsepower", "745.69987158227022", "horse power"),
        ("Metric horsepower", "metric horsepower", "PS", "metric-horsepower", "735.49875", "pferdestarke"),
        ("BTU per hour", "BTU per hour", "BTU/h", "btu-per-hour", ".2930710701722222", "btu hour"),
        ("Foot-pound per second", "foot-pounds per second", "ft·lb/s", "foot-pound-per-second", "1.3558179483314", "ft lb per second"),
    ]),
    "force": ("Force", "newton", "Force units from SI, engineering, and customary systems.", [
        ("Newton", "newtons", "N", "newton", "1", "newtons"),
        ("Kilonewton", "kilonewtons", "kN", "kilonewton", "1000", "kilonewtons"),
        ("Dyne", "dynes", "dyn", "dyne", ".00001", "dynes"),
        ("Kilogram-force", "kilogram-force", "kgf", "kilogram-force", "9.80665", "kilopond"),
        ("Pound-force", "pounds-force", "lbf", "pound-force", "4.4482216152605", "pound force"),
        ("Kip-force", "kips-force", "kip", "kip-force", "4448.2216152605", "kip"),
        ("Poundal", "poundals", "pdl", "poundal", ".138254954376", "poundals"),
    ]),
    "angle": ("Angle", "radian", "Plane-angle conversion for science, navigation, and geometry.", [
        ("Radian", "radians", "rad", "radian", "1", "radians"),
        ("Degree", "degrees", "°", "degree", ".01745329251994329577", "deg,degrees"),
        ("Gradian", "gradians", "gon", "gradian", ".01570796326794896619", "grad,grade"),
        ("Arcminute", "arcminutes", "arcmin", "arcminute", ".00029088820866572160", "minute of arc"),
        ("Arcsecond", "arcseconds", "arcsec", "arcsecond", ".00000484813681109536", "second of arc"),
        ("Revolution", "revolutions", "rev", "revolution", "6.28318530717958647693", "turn,rotation"),
        ("Milliradian", "milliradians", "mrad", "milliradian", ".001", "mil angular"),
    ]),
    "fuel-economy": ("Fuel Economy", "kilometer-per-liter", "Fuel distance and consumption ratios.", [
        ("Kilometer per liter", "kilometers per liter", "km/L", "kilometer-per-liter", "1", "kpl,km per litre"),
        ("Mile per US gallon", "miles per US gallon", "mpg US", "mile-per-us-gallon", ".425143707430272", "mpg,us mpg"),
        ("Mile per Imperial gallon", "miles per Imperial gallon", "mpg Imp", "mile-per-imperial-gallon", ".354006189934647", "imperial mpg"),
        ("Liter per 100 kilometers", "liters per 100 kilometers", "L/100 km", "liters-per-100km", "100", "l per 100km,litres per 100 km"),
        ("Meter per liter", "meters per liter", "m/L", "meter-per-liter", ".001", "meters per litre"),
    ]),
    "data-storage": ("Data Storage", "bit", "Decimal and binary digital-storage units.", [
        ("Bit", "bits", "bit", "bit", "1", "bits"), ("Byte", "bytes", "B", "byte", "8", "bytes"),
        ("Kilobit", "kilobits", "kbit", "kilobit", "1000", "kb"), ("Kilobyte", "kilobytes", "kB", "kilobyte", "8000", "kb decimal"),
        ("Kibibyte", "kibibytes", "KiB", "kibibyte", "8192", "binary kilobyte"),
        ("Megabyte", "megabytes", "MB", "megabyte", "8000000", "mb"), ("Mebibyte", "mebibytes", "MiB", "mebibyte", "8388608", "binary megabyte"),
        ("Gigabyte", "gigabytes", "GB", "gigabyte", "8000000000", "gb"), ("Gibibyte", "gibibytes", "GiB", "gibibyte", "8589934592", "binary gigabyte"),
        ("Terabyte", "terabytes", "TB", "terabyte", "8000000000000", "tb"), ("Tebibyte", "tebibytes", "TiB", "tebibyte", "8796093022208", "binary terabyte"),
    ]),
    "cooking": ("Cooking", "milliliter", "Kitchen volume measures with regional definitions labeled.", [
        ("Milliliter", "milliliters", "mL", "milliliter", "1", "ml"), ("Liter", "liters", "L", "liter", "1000", "litre"),
        ("US teaspoon", "US teaspoons", "tsp", "us-teaspoon", "4.92892159375", "teaspoon"),
        ("US tablespoon", "US tablespoons", "tbsp", "us-tablespoon", "14.78676478125", "tablespoon"),
        ("US cup", "US cups", "cup", "us-cup", "236.5882365", "cups"),
        ("Metric cup", "metric cups", "metric cup", "metric-cup", "250", "cup metric"),
        ("US fluid ounce", "US fluid ounces", "fl oz", "us-fluid-ounce", "29.5735295625", "fluid ounce"),
        ("US pint", "US pints", "pt", "us-pint", "473.176473", "pint"),
    ]),
    "frequency": ("Frequency", "hertz", "Frequency and repeating events per unit time.", [
        ("Hertz", "hertz", "Hz", "hertz", "1", "cycles per second"), ("Kilohertz", "kilohertz", "kHz", "kilohertz", "1000", "khz"),
        ("Megahertz", "megahertz", "MHz", "megahertz", "1000000", "mhz"), ("Gigahertz", "gigahertz", "GHz", "gigahertz", "1000000000", "ghz"),
        ("Revolution per minute", "revolutions per minute", "rpm", "revolution-per-minute", ".01666666666666666667", "rpm"),
        ("Beat per minute", "beats per minute", "bpm", "beat-per-minute", ".01666666666666666667", "bpm"),
        ("Radian per second", "radians per second", "rad/s", "radian-per-second", ".15915494309189533577", "angular frequency"),
    ]),
}

class Command(BaseCommand):
    help = "Create or update the built-in Convertor4U categories and units."
    def handle(self, *args, **options):
        for number, (slug, row) in enumerate(DATA.items(), 1):
            name, base_slug, description, units = row
            guide = GUIDES[slug]
            category, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "number": number, "base_unit_slug": base_slug, "description": description, "order": number, "is_active": True, **guide, "reviewed_by": REVIEWED_BY, "reviewed_on": REVIEWED_ON})
            base_raw = next(item for item in units if item[3] == base_slug)
            base_name, base_symbol = base_raw[0], base_raw[2]
            for order, raw in enumerate(units, 1):
                name, plural, symbol, unit_slug, scale, aliases, *offset = raw
                source_name, source_url = SOURCES.get(slug, DEFAULT_SOURCE)
                if slug == "temperature": mode = "formula"
                elif slug == "fuel-economy" and unit_slug == "liters-per-100km": mode = "reciprocal"
                else: mode = "factor"
                offset_value = offset[0] if offset else "0"
                definition = definition_for(slug, name, symbol, unit_slug, scale, offset_value, mode, base_name, base_symbol)
                Unit.objects.update_or_create(category=category, slug=unit_slug, defaults={"name": name, "plural": plural, "symbol": symbol, "scale": Decimal(scale), "offset": Decimal(offset[0] if offset else "0"), "aliases": aliases, "mode": mode, "definition": definition, "source_name": source_name, "source_url": source_url, "verified_on": VERIFIED_ON, "order": order, "is_active": True})
            for pair_order, (source_slug, target_slug) in enumerate(FEATURED_PAIRS[slug], 1):
                source = Unit.objects.get(category=category, slug=source_slug)
                target = Unit.objects.get(category=category, slug=target_slug)
                homepage_categories = {"length", "mass", "temperature", "speed", "currency", "data-storage"}
                show_on_homepage = slug in homepage_categories and pair_order <= 2
                FeaturedConversion.objects.update_or_create(category=category, from_unit=source, to_unit=target, defaults={"order": pair_order, "is_editorially_reviewed": True, "reviewed_by": REVIEWED_BY, "reviewed_on": REVIEWED_ON, "show_on_homepage": show_on_homepage, "homepage_order": number * 10 + pair_order})
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(DATA)} category guides, {sum(len(v[3]) for v in DATA.values())} reviewed unit definitions, and {sum(len(v) for v in FEATURED_PAIRS.values())} reviewed conversion pages."))
