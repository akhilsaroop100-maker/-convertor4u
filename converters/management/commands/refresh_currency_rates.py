from django.core.management.base import BaseCommand, CommandError

from converters.currency import CurrencyServiceError, latest_rates
from converters.models import Category


class Command(BaseCommand):
    help = "Refresh and persist the latest rates for every active seeded currency."

    def handle(self, *args, **options):
        try:
            category = Category.objects.get(slug="currency", is_active=True)
        except Category.DoesNotExist as exc:
            raise CommandError("Seed the currency category before refreshing rates.") from exc
        codes = list(category.units.filter(is_active=True).values_list("symbol", flat=True))
        refreshed = 0
        try:
            for base in codes:
                quotes = [code for code in codes if code != base]
                latest_rates(base, quotes)
                refreshed += len(quotes)
        except CurrencyServiceError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Refreshed {refreshed} currency pairs."))
