from django.contrib import admin
from .models import Category, CorrectionReport, CurrencyRate, FeaturedConversion, Unit

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ("name", "symbol", "slug", "mode", "scale", "offset", "order", "is_active")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "number", "base_unit_slug", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (UnitInline,)
    fieldsets = (
        ("Directory", {"fields": ("name", "slug", "number", "description", "base_unit_slug", "order", "is_active")}),
        ("Educational guide", {"fields": ("guide_intro", "real_world_uses", "rounding_guidance", "regional_notes", "common_mistakes", "faq")}),
        ("Editorial review", {"fields": ("reviewed_by", "reviewed_on")}),
    )

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "category", "mode", "verified_on", "is_active")
    list_filter = ("category", "mode", "is_active")
    search_fields = ("name", "plural", "symbol", "aliases")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(FeaturedConversion)
class FeaturedConversionAdmin(admin.ModelAdmin):
    list_display = ("category", "from_unit", "to_unit", "is_editorially_reviewed", "show_on_homepage", "homepage_order", "reviewed_on", "order")
    list_filter = ("category", "is_editorially_reviewed", "show_on_homepage")
    list_editable = ("is_editorially_reviewed", "show_on_homepage", "homepage_order", "order")
    autocomplete_fields = ("from_unit", "to_unit")

@admin.register(CorrectionReport)
class CorrectionReportAdmin(admin.ModelAdmin):
    list_display = ("subject", "email", "page_url", "created_at", "resolved")
    list_filter = ("resolved", "created_at")
    search_fields = ("subject", "message", "email", "page_url")
    readonly_fields = ("created_at",)

@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ("base", "quote", "rate", "rate_date", "fetched_at")
    search_fields = ("base", "quote")
    readonly_fields = ("fetched_at",)
