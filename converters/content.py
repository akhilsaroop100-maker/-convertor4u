from decimal import Decimal


EXAMPLE_VALUES = {
    "length": Decimal("5"), "mass": Decimal("75"), "temperature": Decimal("20"),
    "area": Decimal("100"), "volume": Decimal("2"), "time": Decimal("8"),
    "speed": Decimal("100"), "pressure": Decimal("32"), "currency": Decimal("100"),
    "energy": Decimal("1"), "power": Decimal("5"), "force": Decimal("100"),
    "angle": Decimal("90"), "fuel-economy": Decimal("7"),
    "data-storage": Decimal("256"), "cooking": Decimal("1"), "frequency": Decimal("60"),
}

USE_CASES = {
    "length": "checking a room dimension, product size, route distance, or drawing scale",
    "mass": "comparing a person's mass, a recipe quantity, luggage allowance, or shipping weight",
    "temperature": "reading a weather forecast, oven setting, laboratory result, or equipment limit",
    "area": "estimating flooring, land size, paint coverage, or a property listing",
    "volume": "measuring a drink, fuel tank, container, or laboratory liquid",
    "time": "planning a shift, journey, workout, or project duration",
    "speed": "comparing a road speed, running pace, vessel speed, or wind report",
    "pressure": "checking a tire, weather report, process gauge, or engineering specification",
    "currency": "estimating a travel budget or comparing an overseas price",
    "energy": "comparing an electricity bill, battery capacity, food energy, or heating requirement",
    "power": "comparing an appliance, motor, engine, solar array, or heating system",
    "force": "reading a load specification, test result, structural calculation, or tool rating",
    "angle": "working with a drawing, bearing, machine setting, or rotation",
    "fuel-economy": "comparing vehicle efficiency across regional specifications",
    "data-storage": "checking a download, storage device, memory allocation, or backup size",
    "cooking": "adapting a recipe written with a different measuring system",
    "frequency": "comparing rotation, audio, radio, processor, or repeating-event rates",
}

PAIR_WARNINGS = {
    "temperature": "Temperature scales have offsets, so multiplying by a single ratio is usually wrong.",
    "area": "Area factors are squared: a linear foot-to-meter factor cannot be used unchanged for square feet.",
    "volume": "US and Imperial gallons and fluid ounces are different units; check the regional label.",
    "time": "This converter treats a year as the labeled fixed duration, not a variable calendar interval.",
    "pressure": "Do not mix gauge pressure with absolute pressure; the unit conversion alone does not add atmospheric pressure.",
    "currency": "A reference rate is not a guaranteed transaction quote; banks and card providers may add spreads and fees.",
    "energy": "Power and energy are different: kilowatts measure a rate, while kilowatt-hours measure an amount of energy.",
    "power": "Do not confuse kW with kWh: power is a rate and energy also depends on elapsed time.",
    "force": "Kilogram is mass, while kilogram-force is force under standard gravity; they are not interchangeable.",
    "angle": "Keep angular units separate from angular speed; radians and radians per second describe different quantities.",
    "fuel-economy": "L/100 km runs in the opposite direction to mpg or km/L: a lower L/100 km value means better economy.",
    "data-storage": "Uppercase B means byte and lowercase b means bit; also distinguish decimal GB from binary GiB.",
    "cooking": "Volume conversion cannot determine ingredient mass without the ingredient's density.",
    "frequency": "Radians per second is angular frequency; converting it to hertz requires the 2π relationship.",
}

# Hand-written copy for the highest-value routes. These entries deliberately add
# pair-specific context beyond the general category guide and calculator output.
PRIORITY_EDITORIAL = {
    ("length", "cm", "inches"): {
        "explanation": "Centimeters are common on metric product drawings, while inches dominate many screen, hardware, and clothing dimensions in the United States. The relationship is fixed by definition: one inch is exactly 2.54 centimeters, so this conversion does not depend on a measured or changing rate.",
        "example": "A 5 cm object is {result} in long. That is useful when checking small product dimensions, but a retailer may round the listed inch size, so keep the manufacturer’s tolerance separate from the mathematical conversion.",
        "mistake": "Do not divide by 2.5 as a final answer. That shortcut is useful for a quick estimate, but the exact divisor is 2.54 and the difference becomes noticeable over longer lengths.",
        "faqs": [("Why is 2.54 used?", "International standards define one inch as exactly 25.4 millimeters, which is exactly 2.54 centimeters."), ("Is 10 cm exactly 4 inches?", "No. Ten centimeters is about 3.937 inches; four inches is exactly 10.16 centimeters.")],
    },
    ("length", "meter", "foot"): {
        "explanation": "Meters are the SI unit used for building plans and athletics, while feet remain familiar in US property and height descriptions. Since one foot is exactly 0.3048 meter, the page divides the meter value by 0.3048 using decimal arithmetic.",
        "example": "A length of 5 m is {result} ft. For room dimensions this is roughly 16 ft 5 in, but construction work should retain the decimal result before converting any remainder into inches.",
        "mistake": "A decimal foot is not a feet-and-inches notation. For example, 5.5 ft means 5 ft 6 in, not 5 ft 5 in, because the decimal part is a fraction of twelve inches.",
        "faqs": [("How many feet are in one meter?", "One meter is approximately 3.28084 feet."), ("Can I use this for a person’s height?", "Yes. Convert to decimal feet first, then multiply the fractional foot by 12 to obtain inches.")],
    },
    ("length", "kilometer", "mile"): {
        "explanation": "Kilometers appear on road signs in most countries, while statute miles are used for US and UK road distances. A statute mile is exactly 1,609.344 meters, so the kilometer-to-mile result follows a fixed legal definition.",
        "example": "A 5 km race is {result} mi, commonly described as about 3.1 miles. GPS watches may show a slightly different distance because route measurement and positioning error are separate from unit conversion.",
        "mistake": "Do not confuse the statute mile used here with a nautical mile. A nautical mile is exactly 1.852 kilometers and is used in marine and aviation navigation.",
        "faqs": [("Is 5 km the same as 3 miles?", "Not exactly. Three statute miles is about 4.828 kilometers, while 5 kilometers is about 3.107 miles."), ("What factor gives a quick estimate?", "Multiplying kilometers by 0.62 gives a useful estimate; use the calculator for a more precise result.")],
    },
    ("length", "mile", "kilometer"): {
        "explanation": "This page converts international statute miles to SI kilometers using the exact definition of 1 mile = 1.609344 kilometers. It is suitable for road distance, running, and mapping, but not for nautical-mile distances.",
        "example": "A 5 mi journey is {result} km. That makes a five-mile training run a little over eight kilometers before any GPS or course-measurement variation is considered.",
        "mistake": "Multiplying by 1.6 is a good mental estimate but not an exact conversion. Use 1.609344 when mileage reimbursement, surveying, or race distances need greater precision.",
        "faqs": [("How many kilometers are in a mile?", "One international statute mile is exactly 1.609344 kilometers."), ("Is a UK road mile different from a US mile?", "Modern UK and US road distances use the same international statute mile.")],
    },
    ("mass", "kilogram", "pound"): {
        "explanation": "Kilograms are SI mass units; pounds are common for body weight, luggage, and goods in the United States and United Kingdom. The international avoirdupois pound is exactly 0.45359237 kilogram, giving this page a fixed conversion rather than an estimate.",
        "example": "A mass of 75 kg is {result} lb. A bathroom or luggage scale may show fewer digits because its measurement resolution is usually much coarser than the conversion factor.",
        "mistake": "Do not use 2.2 when a precise shipping or technical value is required. It is a convenient estimate, but the full relationship is about 2.20462262 pounds per kilogram.",
        "faqs": [("Is kilogram a mass or a weight?", "The kilogram is a unit of mass. Everyday scales infer mass from force under local gravity."), ("How do I estimate kilograms in pounds mentally?", "Double the kilogram value and add roughly ten percent; use the exact converter for the final value.")],
    },
    ("mass", "pound", "kilogram"): {
        "explanation": "The pound on this page is the international avoirdupois pound used for ordinary body, parcel, and product mass. It has the exact definition 0.45359237 kilogram, so laboratory and shipping calculations can retain more precision than typical display scales.",
        "example": "A 75 lb item is {result} kg. Airline baggage rules usually specify a rounded limit in both units, so follow the carrier’s stated limit rather than relying on a rounded conversion alone.",
        "mistake": "Pound-mass and pound-force describe different quantities. This page converts ordinary pounds of mass, not the pound-force used in engineering loads.",
        "faqs": [("Is one pound exactly 0.45 kg?", "No. That is a rough estimate; one international avoirdupois pound is exactly 0.45359237 kilogram."), ("Why can a baggage limit look inconsistent?", "Carriers often publish separately rounded kilogram and pound limits rather than mathematically identical thresholds.")],
    },
    ("temperature", "celsius", "fahrenheit"): {
        "explanation": "Celsius and Fahrenheit have different zero points and degree sizes. The converter multiplies Celsius by 9/5 and then adds 32; it cannot use a simple factor through zero as length or mass conversions do.",
        "example": "A temperature of 20 °C is {result} °F, a typical mild indoor or outdoor temperature. Weather stations and thermostats may round to whole degrees, so their displayed reverse conversion may differ slightly.",
        "mistake": "Do not only multiply by 1.8; the 32-degree offset is essential. Also remember that a change of 1 °C equals a change of 1.8 °F even though the absolute readings need the offset.",
        "faqs": [("At what temperature are Celsius and Fahrenheit equal?", "They have the same numerical value at −40 degrees."), ("Why does 0 °C become 32 °F?", "The scales use different reference points: water freezes at 0 °C and 32 °F under standard conditions.")],
    },
    ("temperature", "fahrenheit", "celsius"): {
        "explanation": "To convert Fahrenheit to Celsius, subtract 32 first and then multiply by 5/9. This accounts for both the displaced zero point and the smaller size of a Fahrenheit degree.",
        "example": "A reading of 20 °F is {result} °C, which is below water’s freezing point. For medical temperatures, use the precision and method recommended for the thermometer rather than over-interpreting extra calculator digits.",
        "mistake": "Order matters: subtract 32 before multiplying by 5/9. Multiplying the original Fahrenheit value first produces an incorrect temperature.",
        "faqs": [("What is 32 °F in Celsius?", "Thirty-two degrees Fahrenheit is 0 degrees Celsius under the scale definition."), ("Is a Fahrenheit degree the same size as a Celsius degree?", "No. A change of 1 °F equals a change of 5/9 °C.")],
    },
    ("temperature", "kelvin", "celsius"): {
        "explanation": "Kelvin and Celsius increments are the same size, but their zero points differ. Subtract exactly 273.15 from kelvin to obtain degrees Celsius; kelvin values are written without a degree symbol.",
        "example": "A temperature of 20 K is {result} °C, an extremely cold value close to absolute zero. This example is scientific rather than a typical weather temperature.",
        "mistake": "Do not write °K and do not treat kelvin as a ratio to Celsius. The correct symbol is K, and conversion requires the 273.15 offset.",
        "faqs": [("Can kelvin be negative?", "Ordinary thermodynamic temperature cannot be below absolute zero, 0 K."), ("Why are kelvin and Celsius degree changes equal?", "Both scales use the same interval size; only their zero points differ by 273.15.")],
    },
    ("area", "square-meter", "square-foot"): {
        "explanation": "Square meters measure area in SI plans and listings, while square feet are common in US property and flooring work. Because area is two-dimensional, the exact meter-to-foot relationship is squared, giving roughly 10.7639 square feet per square meter.",
        "example": "An area of 100 m² is {result} ft², a plausible apartment or small-home floor area. Purchase quantities should also include the installer’s waste allowance; unit conversion does not add it automatically.",
        "mistake": "Do not use 3.28084, the linear feet-per-meter factor, for area. Squaring the linear relationship is what produces about 10.7639 ft² per m².",
        "faqs": [("Is 10 m by 10 m equal to 100 m²?", "Yes. Its converted area is about 1,076.39 ft²."), ("Should flooring orders use the exact converted area?", "Use the converted measured area, then apply the separate waste or cutting allowance recommended for the material.")],
    },
    ("area", "acre", "hectare"): {
        "explanation": "Acres remain common in US and UK land descriptions; hectares are widely used for metric agriculture and large property areas. One international acre is exactly 4,046.8564224 square meters, so it equals exactly 0.40468564224 hectare.",
        "example": "A 100 acre property is {result} ha. Boundary surveys and title documents control the legal area; converting the stated number does not correct an imprecise or disputed measurement.",
        "mistake": "Do not assume one hectare equals two acres exactly. One hectare is about 2.47105 acres, and the difference matters for land valuation or application rates.",
        "faqs": [("How many hectares are in one acre?", "One international acre is exactly 0.40468564224 hectare."), ("Are all historical acres identical?", "No. Historical and regional acre definitions varied; modern calculations normally mean the international acre.")],
    },
    ("volume", "liter", "us-gallon"): {
        "explanation": "Liters are metric volume units, while the US liquid gallon is used for fuel and containers in the United States. One US liquid gallon is exactly 3.785411784 liters; this is not the larger Imperial gallon.",
        "example": "A 2 L container holds {result} US gal. Product labels may round both quantities independently, so package markings are not always exact reverse conversions.",
        "mistake": "Check the word ‘US’ before using a gallon result. One Imperial gallon is 4.54609 liters and would produce a materially different answer.",
        "faqs": [("How many US gallons are in one liter?", "One liter is approximately 0.264172 US liquid gallon."), ("Does this convert dry gallons?", "No. This page uses the US liquid gallon, not the less common US dry gallon.")],
    },
    ("volume", "us-gallon", "liter"): {
        "explanation": "This route converts US liquid gallons to liters using the exact definition 1 US gal = 3.785411784 L. It is appropriate for US fuel economy, tank capacity, and liquid packaging, but not Imperial gallons.",
        "example": "A 2 US gal container holds {result} L. Usable tank capacity can differ from its nominal label, which is a product specification issue rather than a conversion error.",
        "mistake": "Do not use 4.54609 unless the source explicitly says Imperial or UK gallon. Mixing gallon systems causes an error of about twenty percent.",
        "faqs": [("How many liters are in five US gallons?", "Five US liquid gallons equal exactly 18.92705892 liters."), ("Are US fuel gallons liquid gallons?", "Yes. Retail motor fuel in the United States is measured in US liquid gallons.")],
    },
    ("speed", "kilometer-per-hour", "mile-per-hour"): {
        "explanation": "Kilometers per hour appear on most road signs worldwide, while miles per hour are standard for road speeds in the United States and United Kingdom. The conversion combines the exact kilometer and international-mile definitions.",
        "example": "A speed of 100 km/h is {result} mph, commonly rounded to about 62 mph. A vehicle speedometer may intentionally read slightly high and should not be used to judge the converter’s accuracy.",
        "mistake": "Do not treat 100 km/h as 60 mph exactly. That is a useful road-speed estimate, but the precise result is about 62.137 mph.",
        "faqs": [("What is a quick km/h to mph estimate?", "Multiply by 0.62 for a quick estimate; use the exact result when precision matters."), ("Does this convert running pace?", "It converts speed. Minutes per kilometer and minutes per mile are reciprocal pace measures and need a separate calculation.")],
    },
    ("speed", "mile-per-hour", "kilometer-per-hour"): {
        "explanation": "Miles per hour are converted to kilometers per hour by multiplying by exactly 1.609344. The mile used is the international statute mile, not the nautical mile used for knots.",
        "example": "A speed of 100 mph is {result} km/h. This is well above ordinary road limits in many countries, so the example is mathematical rather than driving guidance.",
        "mistake": "Do not convert mph to km/h with 1.5 when accuracy matters. Multiplying by 1.6 is a closer mental estimate, while 1.609344 is exact.",
        "faqs": [("What is 60 mph in km/h?", "Sixty miles per hour equals 96.56064 kilometers per hour."), ("Is mph the same as a knot?", "No. A knot is one nautical mile per hour and is about 1.15078 mph.")],
    },
    ("pressure", "psi", "kilopascal"): {
        "explanation": "Pounds per square inch are common on US tire and equipment gauges; kilopascals are the SI-derived values used in many manuals. The conversion changes only the unit scale and does not change whether a reading is gauge or absolute pressure.",
        "example": "A tire reading of 32 psi is {result} kPa. Inflate to the vehicle manufacturer’s cold-tire specification, not the tire sidewall maximum or a generic converted example.",
        "mistake": "Do not mix gauge pressure with absolute pressure. Most tire gauges read above atmospheric pressure, while some engineering data uses absolute pressure; unit conversion alone cannot reconcile them.",
        "faqs": [("Is 1 psi about 7 kPa?", "Yes for estimation: 1 psi is approximately 6.89476 kPa."), ("Why does tire pressure change after driving?", "Heating raises the air temperature and pressure; compare pressures under the conditions specified by the manufacturer.")],
    },
    ("currency", "usd", "zar"): {
        "explanation": "US dollar to South African rand results use the dated Frankfurter reference rate shown on the page. Unlike fixed measurement conversions, exchange rates move over time and the displayed rate is an informational midpoint rather than a guaranteed bank or card quote.",
        "example": "At the displayed reference rate, USD {value} converts to approximately ZAR {result}. A real purchase or transfer can settle at a different amount after provider spread, fees, timing, and card-network rules.",
        "mistake": "Do not budget from the reference result alone. Check whether your provider adds a percentage spread, fixed fee, cash-withdrawal fee, or delayed settlement rate.",
        "faqs": [("How current is the USD/ZAR rate?", "The page labels the reference date and indicates if a cached last-known rate is being used."), ("Will my bank give this exact rate?", "Usually not. Banks, cards, and transfer services may use different timestamps and add fees or a spread.")],
    },
    ("currency", "eur", "usd"): {
        "explanation": "Euro to US dollar conversion uses a dated institutional reference rate supplied through Frankfurter. The rate is useful for comparison and planning but is not a live executable foreign-exchange quote.",
        "example": "At the displayed reference rate, EUR {value} converts to approximately USD {result}. The amount charged for a hotel or online order may differ because the merchant, card network, or bank chooses the conversion path and fees.",
        "mistake": "Avoid converting twice through a card’s dynamic currency conversion option without comparing costs. Merchant-offered home-currency prices can embed a separate markup.",
        "faqs": [("Why does EUR/USD change?", "Currency values respond to market supply, interest-rate expectations, economic news, and trading conditions."), ("What does a EUR/USD rate above 1 mean?", "It means one euro converts to more than one US dollar at that reference rate.")],
    },
    ("energy", "kilowatt-hour", "joule"): {
        "explanation": "A kilowatt-hour measures energy delivered by one kilowatt for one hour. Since one watt equals one joule per second and one hour has 3,600 seconds, one kilowatt-hour equals exactly 3.6 million joules.",
        "example": "An energy amount of 1 kWh is {result} J. Electricity bills normally retain kWh because joules would create very large numbers for household use.",
        "mistake": "Do not confuse kWh with kW. A 2 kW appliance uses 1 kWh in half an hour only if it runs continuously at that power.",
        "faqs": [("Is a kilowatt-hour a unit of power?", "No. It is energy; kilowatt is power, while multiplying power by time gives energy."), ("Why is 1 kWh 3.6 MJ?", "One kilowatt is 1,000 joules per second, and an hour is 3,600 seconds, producing 3,600,000 joules.")],
    },
    ("data-storage", "gigabyte", "gibibyte"): {
        "explanation": "A decimal gigabyte contains exactly 1,000,000,000 bytes, while a binary gibibyte contains exactly 1,073,741,824 bytes. Drive manufacturers commonly use GB; some operating systems report binary-sized quantities even when the interface label is ambiguous.",
        "example": "A nominal 256 GB storage amount is {result} GiB before formatting, system files, recovery partitions, and reserved space reduce the capacity available to the user.",
        "mistake": "Do not assume GB and GiB are alternative spellings for the same amount. Their difference grows with capacity, and it is separate from formatting overhead.",
        "faqs": [("Why does a 256 GB drive appear smaller?", "Part comes from decimal GB versus binary GiB, and additional space can be used by formatting and system partitions."), ("Which prefixes are binary?", "KiB, MiB, GiB, and TiB are binary prefixes based on powers of 1,024.")],
    },
}


def pair_editorial(category, source, target, example_value, example_result):
    exactness = "the stored factor and offset definitions"
    if category.slug == "currency":
        exactness = "the dated reference exchange rate shown beside the result"
    elif source.mode == "reciprocal" or target.mode == "reciprocal":
        exactness = "the reciprocal fuel-consumption relationship"
    elif source.mode == "formula" or target.mode == "formula":
        exactness = "the scale offsets shown in the formula"

    priority = PRIORITY_EDITORIAL.get((category.slug, source.slug, target.slug))
    explanation = (
        f"This page converts {source.plural} ({source.symbol}) to {target.plural} ({target.symbol}). "
        f"Convertor4U first interprets the input using {source.name}'s definition, then expresses the same "
        f"quantity in {target.name}. The result is calculated from {exactness}, not from a rounded lookup table."
    )
    example = (
        f"For {USE_CASES.get(category.slug, 'a practical comparison')}, an input of {example_value} "
        f"{source.symbol} converts to {example_result} {target.symbol}. Keep extra digits while calculating, "
        "then round only the final value to the precision the task actually needs."
    )
    mistake = PAIR_WARNINGS.get(
        category.slug,
        f"A common mistake is attaching {target.symbol} to the original number without applying the full {source.symbol}-to-{target.symbol} factor.",
    )
    faqs = [
        {
            "question": f"How do I convert {source.plural} to {target.plural}?",
            "answer": f"Enter the {source.symbol} value in the calculator. It applies {exactness} and returns the equivalent in {target.symbol}; the formula and common-value table are shown on this page.",
        },
        {
            "question": f"Is the {source.symbol} to {target.symbol} conversion exact?",
            "answer": "Defined measurement relationships are calculated with decimal arithmetic from stored standards. The displayed answer may be rounded for readability. Currency results instead depend on the dated reference rate shown.",
        },
        {
            "question": "How many decimal places should I keep?",
            "answer": category.rounding_guidance or "Keep at least one or two guard digits during the calculation and round the final result to match the precision of the original measurement.",
        },
        {
            "question": "What should I check before using the result?",
            "answer": mistake,
        },
    ]
    if priority:
        values = {"value": example_value, "result": example_result, "source": source.symbol, "target": target.symbol}
        explanation = priority["explanation"].format(**values)
        example = priority["example"].format(**values)
        mistake = priority["mistake"].format(**values)
        custom_faqs = [{"question": question, "answer": answer} for question, answer in priority["faqs"]]
        faqs = custom_faqs + faqs[:2]
    return {"explanation": explanation, "example": example, "mistake": mistake, "faqs": faqs}
