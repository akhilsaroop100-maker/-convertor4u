from decimal import Decimal
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch
from .currency import convert_currency
from .engine import convert
from .models import Category, CorrectionReport, CurrencyRate, FeaturedConversion, Unit
from .sitemaps import PairSitemap
from . import views

class ConversionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Length", slug="length", number=1, base_unit_slug="meter")
        cls.m = Unit.objects.create(category=cls.cat, name="Meter", plural="meters", symbol="m", slug="meter", scale=1)
        cls.cm = Unit.objects.create(category=cls.cat, name="Centimeter", plural="centimeters", symbol="cm", slug="cm", scale=Decimal(".01"))

    def test_factor_conversion(self): self.assertEqual(convert(100, self.cm, self.m), Decimal("1"))
    def test_api(self):
        r = self.client.get(reverse("convert_api"), {"category":"length", "from":"cm", "to":"meter", "value":"250"})
        self.assertEqual(r.status_code, 200); self.assertEqual(r.json()["result"], "2.5")
    def test_units_api_includes_formula_data(self):
        unit = self.client.get("/api/categories/length/units/").json()["units"][0]
        self.assertIn("scale", unit)
        self.assertIn("offset", unit)
    def test_pair_page(self):
        response = self.client.get("/length/cm-to-meter/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content="noindex,follow"')
        self.assertContains(response, 'data-ads-eligible="false"')
    def test_round_trip_and_extreme_values(self):
        for value in (Decimal("-1000000"), Decimal("0"), Decimal("0.0000001"), Decimal("1E20")):
            self.assertEqual(convert(convert(value, self.m, self.cm), self.cm, self.m), value)

class TemperatureTests(TestCase):
    def test_celsius_to_fahrenheit(self):
        cat = Category.objects.create(name="Temperature", slug="temperature", number=2, base_unit_slug="kelvin")
        c = Unit.objects.create(category=cat, name="Celsius", plural="degrees Celsius", symbol="°C", slug="celsius", scale=1, offset=Decimal("273.15"))
        f = Unit.objects.create(category=cat, name="Fahrenheit", plural="degrees Fahrenheit", symbol="°F", slug="fahrenheit", scale=Decimal(5)/9, offset=Decimal("255.37222222222222222222"))
        self.assertAlmostEqual(float(convert(100, c, f)), 212.0, places=8)

class CurrencyTests(TestCase):
    @patch("converters.currency.latest_rate", return_value=(Decimal("18.5"), "2026-08-13", False))
    def test_live_currency_conversion(self, mocked_rate):
        source = type("Currency", (), {"symbol": "USD"})()
        target = type("Currency", (), {"symbol": "ZAR"})()
        result, rate, date, stale = convert_currency("10", source, target)
        self.assertEqual(result, Decimal("185.0"))
        self.assertEqual(date, "2026-08-13")
        self.assertFalse(stale)

class ReciprocalAndQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fuel = Category.objects.create(name="Fuel Economy", slug="fuel-economy", number=30, base_unit_slug="kilometer-per-liter")
        cls.kpl = Unit.objects.create(category=fuel, name="Kilometer per liter", plural="kilometers per liter", symbol="km/L", slug="kilometer-per-liter", scale=1, aliases="kpl")
        cls.l100 = Unit.objects.create(category=fuel, name="Liter per 100 kilometers", plural="liters per 100 kilometers", symbol="L/100 km", slug="liters-per-100km", scale=100, mode="reciprocal", aliases="l per 100km")
        mass = Category.objects.create(name="Mass", slug="mass", number=31, base_unit_slug="kilogram")
        Unit.objects.create(category=mass, name="Kilogram", plural="kilograms", symbol="kg", slug="kilogram", scale=1, aliases="kilos")
        Unit.objects.create(category=mass, name="Pound", plural="pounds", symbol="lb", slug="pound", scale=Decimal(".45359237"), aliases="lbs")

    def test_reciprocal_conversion(self):
        self.assertEqual(convert(Decimal("5"), self.l100, self.kpl), Decimal("20"))
        self.assertEqual(convert(Decimal("20"), self.kpl, self.l100), Decimal("5"))

    def test_natural_language_query(self):
        response = self.client.get("/api/query/", {"q": "72 kg to lb"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "mass")

    def test_compact_natural_language_query(self):
        response = self.client.get("/api/query/", {"q": "72kg to lb"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "mass")

    def test_health_check(self):
        self.assertEqual(self.client.get("/healthz/").json()["status"], "ok")

class ReferencePageTests(TestCase):
    def test_public_reference_pages(self):
        for url in ("/unit-systems/", "/accuracy/", "/contact/", "/about/", "/terms/", "/privacy/", "/site-map/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_home_has_search_metadata(self):
        response = self.client.get("/")
        self.assertContains(response, '<link rel="canonical"')
        self.assertContains(response, 'application/ld+json')
        self.assertContains(response, 'Online Unit Converter')
        self.assertContains(response, 'CONVERTOR<span>4U</span>', count=2)
        self.assertContains(response, 'CONVERTOR4U.COM')
        self.assertNotContains(response, 'CONVERT/26')

    def test_category_links_to_conversion_pages(self):
        category = Category.objects.create(name="Length", slug="length", number=20, base_unit_slug="meter")
        Unit.objects.create(category=category, name="Meter", plural="meters", symbol="m", slug="meter", scale=1)
        Unit.objects.create(category=category, name="Centimeter", plural="centimeters", symbol="cm", slug="cm", scale=Decimal(".01"))
        response = self.client.get("/length/")
        self.assertContains(response, "/length/meter-to-cm/")

class EditorialQualityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_units", verbosity=0)

    def test_all_categories_have_substantial_guides_and_faqs(self):
        categories = Category.objects.all()
        self.assertEqual(categories.count(), 17)
        for category in categories:
            with self.subTest(category=category.slug):
                self.assertGreater(len(category.guide_intro), 100)
                self.assertGreater(len(category.real_world_uses), 100)
                self.assertGreater(len(category.rounding_guidance), 100)
                self.assertGreaterEqual(len(category.faq), 3)
                self.assertTrue(category.reviewed_by)
                self.assertIsNotNone(category.reviewed_on)

    def test_every_unit_definition_is_specific_and_sourced(self):
        self.assertEqual(Unit.objects.count(), 124)
        for unit in Unit.objects.all():
            with self.subTest(unit=f"{unit.category.slug}/{unit.slug}"):
                self.assertGreater(len(unit.definition), 65)
                self.assertNotIn("is used in", unit.definition)
                self.assertTrue(unit.source_name)
                self.assertTrue(unit.source_url)
                self.assertIsNotNone(unit.verified_on)

    def test_reviewed_page_is_indexable_and_in_sitemap(self):
        response = self.client.get("/length/cm-to-inches/")
        self.assertContains(response, "EDITORIALLY REVIEWED")
        self.assertContains(response, 'content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"')
        self.assertContains(response, 'data-ads-eligible="true"')
        self.assertContains(response, "Real-world example")
        self.assertContains(response, "FAQPage")
        self.assertIn(("length", "cm", "inches"), PairSitemap().items())

    def test_unreviewed_page_is_excluded_from_pair_sitemap(self):
        response = self.client.get("/length/yard-to-nautical-mile/")
        self.assertContains(response, 'content="noindex,follow"')
        self.assertNotIn(("length", "yard", "nautical-mile"), PairSitemap().items())

    def test_category_guide_and_visible_faq(self):
        response = self.client.get("/temperature/")
        self.assertContains(response, "Understanding temperature units")
        self.assertContains(response, "Rounding and precision")
        self.assertContains(response, "Temperature conversion FAQs")

    def test_correction_report_submission(self):
        response = self.client.post("/contact/", {
            "name": "Reader", "email": "reader@example.com",
            "page_url": "https://convertor4u.com/length/cm-to-inches/",
            "subject": "Definition question", "message": "Please verify the explanation against the cited source.",
            "website": "",
        })
        self.assertRedirects(response, "/contact/?submitted=1", fetch_redirect_response=False)
        self.assertEqual(CorrectionReport.objects.count(), 1)

    def test_compound_feet_and_inches_query(self):
        response = self.client.get("/api/query/", {"q": "5 ft 11 in to cm"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["input"], "5 ft 11 in")
        self.assertEqual(response.json()["result"], "180.34")

    def test_admin_featured_pairs_drive_homepage(self):
        response = self.client.get("/")
        self.assertContains(response, "EDITOR-SELECTED CONVERSIONS")
        self.assertContains(response, "/length/cm-to-inches/")
        self.assertContains(response, "These links are managed and reviewed in Django admin.")

    def test_visible_alias_search_and_local_clear_controls(self):
        response = self.client.get("/")
        self.assertContains(response, "unit-search-results")
        self.assertContains(response, "CLEAR HISTORY")
        self.assertContains(response, "CLEAR FAVORITES")

    def test_decimal_api_preserves_small_exact_result(self):
        response = self.client.get("/api/convert/", {"category": "length", "from": "millimeter", "to": "meter", "value": "0.0000001"})
        self.assertEqual(response.json()["result"], "1.00000000e-10")
        self.assertEqual(response.json()["provider_status"], "exact")

    @patch("converters.views.convert_currency_multi")
    def test_currency_multi_convert(self, mocked_multi):
        category = Category.objects.get(slug="currency")
        source = category.units.get(slug="usd")
        targets = list(category.units.exclude(pk=source.pk)[:10])
        mocked_multi.return_value = ([(unit, Decimal("10") * (index + 1)) for index, unit in enumerate(targets)], "2026-08-15", False)
        response = self.client.get("/api/multi-convert/", {"category": "currency", "from": "usd", "value": "10"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provider_status"], "live")
        self.assertEqual(len(response.json()["items"]), 10)

    @patch("converters.views.historical_rates")
    def test_currency_history_endpoint(self, mocked_history):
        mocked_history.return_value = [{"date": "2026-08-14", "rate": "18.4"}, {"date": "2026-08-15", "rate": "18.5"}]
        response = self.client.get("/api/currency/history/", {"from": "usd", "to": "zar", "days": "30"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["points"]), 2)

    @patch("converters.management.commands.refresh_currency_rates.latest_rates")
    def test_scheduled_refresh_command(self, mocked_rates):
        mocked_rates.return_value = ({}, "2026-08-15", False)
        call_command("refresh_currency_rates", verbosity=0)
        self.assertEqual(mocked_rates.call_count, 12)

    @override_settings(DEBUG=False)
    def test_custom_404_page(self):
        response = self.client.get("/not-a-real-converter-page/extra/missing/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "That page is off the scale.", status_code=404)

    def test_custom_500_page(self):
        response = views.server_error(RequestFactory().get("/error/"))
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"calculation desk hit a snag", response.content)

    @override_settings(MAINTENANCE_MODE=True)
    def test_maintenance_mode_and_health_exception(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "Brief calibration in progress.", status_code=503)
        self.assertEqual(response["Retry-After"], "900")
        self.assertEqual(self.client.get("/healthz/").status_code, 200)
