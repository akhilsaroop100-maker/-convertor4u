from decimal import Decimal
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    number = models.PositiveSmallIntegerField(unique=True)
    description = models.TextField(blank=True)
    guide_intro = models.TextField(blank=True)
    real_world_uses = models.TextField(blank=True)
    rounding_guidance = models.TextField(blank=True)
    regional_notes = models.TextField(blank=True)
    common_mistakes = models.TextField(blank=True)
    faq = models.JSONField(default=list, blank=True)
    reviewed_by = models.CharField(max_length=120, blank=True)
    reviewed_on = models.DateField(null=True, blank=True)
    base_unit_slug = models.SlugField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "categories"

    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("category", args=[self.slug])

class Unit(models.Model):
    FACTOR, FORMULA, RECIPROCAL = "factor", "formula", "reciprocal"
    MODES = [(FACTOR, "Factor"), (FORMULA, "Formula (scale + offset)"), (RECIPROCAL, "Reciprocal")]
    category = models.ForeignKey(Category, related_name="units", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    plural = models.CharField(max_length=80)
    symbol = models.CharField(max_length=20)
    slug = models.SlugField()
    aliases = models.CharField(max_length=250, blank=True, help_text="Comma-separated search aliases")
    mode = models.CharField(max_length=12, choices=MODES, default=FACTOR)
    scale = models.DecimalField(max_digits=40, decimal_places=20, default=Decimal("1"), help_text="base = value × scale + offset")
    offset = models.DecimalField(max_digits=40, decimal_places=20, default=Decimal("0"))
    definition = models.TextField(blank=True)
    source_name = models.CharField(max_length=120, blank=True)
    source_url = models.URLField(blank=True)
    verified_on = models.DateField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")
        constraints = [models.UniqueConstraint(fields=("category", "slug"), name="unique_unit_slug_per_category")]

    def __str__(self): return f"{self.name} ({self.symbol})"

class FeaturedConversion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    from_unit = models.ForeignKey(Unit, related_name="featured_from", on_delete=models.CASCADE)
    to_unit = models.ForeignKey(Unit, related_name="featured_to", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    is_editorially_reviewed = models.BooleanField(default=False)
    reviewed_by = models.CharField(max_length=120, blank=True)
    reviewed_on = models.DateField(null=True, blank=True)
    show_on_homepage = models.BooleanField(default=False)
    homepage_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order",)
        constraints = [models.UniqueConstraint(fields=("category", "from_unit", "to_unit"), name="unique_featured_conversion")]
    def __str__(self): return f"{self.from_unit.symbol} → {self.to_unit.symbol}"

class CorrectionReport(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    page_url = models.URLField(blank=True)
    subject = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta: ordering = ("-created_at",)
    def __str__(self): return self.subject

class CurrencyRate(models.Model):
    base = models.CharField(max_length=3)
    quote = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=40, decimal_places=20)
    rate_date = models.DateField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("base", "quote"), name="unique_currency_pair")]
        ordering = ("base", "quote")

    def __str__(self): return f"{self.base}/{self.quote} {self.rate}"
