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


def pair_editorial(category, source, target, example_value, example_result):
    exactness = "the stored factor and offset definitions"
    if category.slug == "currency":
        exactness = "the dated reference exchange rate shown beside the result"
    elif source.mode == "reciprocal" or target.mode == "reciprocal":
        exactness = "the reciprocal fuel-consumption relationship"
    elif source.mode == "formula" or target.mode == "formula":
        exactness = "the scale offsets shown in the formula"

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
    return {"explanation": explanation, "example": example, "mistake": mistake, "faqs": faqs}
