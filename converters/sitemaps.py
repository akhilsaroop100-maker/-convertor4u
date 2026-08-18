from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category, FeaturedConversion

class StaticSitemap(Sitemap):
    priority = 1
    def items(self): return ["home", "unit_systems", "accuracy", "contact", "about", "terms", "privacy", "site_map"]
    def location(self, item): return reverse(item)
class CategorySitemap(Sitemap):
    priority = .8
    def items(self): return Category.objects.filter(is_active=True)
class PairSitemap(Sitemap):
    priority, limit = .7, 10000
    def items(self):
        rows = FeaturedConversion.objects.filter(
            is_editorially_reviewed=True, category__is_active=True,
            from_unit__is_active=True, to_unit__is_active=True,
        ).select_related("category", "from_unit", "to_unit")
        return [(row.category.slug, row.from_unit.slug, row.to_unit.slug) for row in rows]
    def location(self, item): return reverse("conversion", args=[item[0], f"{item[1]}-to-{item[2]}"])
