from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Category", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80, unique=True)), ("slug", models.SlugField(unique=True)),
            ("number", models.PositiveSmallIntegerField(unique=True)), ("description", models.TextField(blank=True)),
            ("base_unit_slug", models.SlugField()), ("order", models.PositiveSmallIntegerField(default=0)),
            ("is_active", models.BooleanField(default=True)),
        ], options={"ordering": ("order", "name"), "verbose_name_plural": "categories"}),
        migrations.CreateModel(name="Unit", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80)), ("plural", models.CharField(max_length=80)),
            ("symbol", models.CharField(max_length=20)), ("slug", models.SlugField()),
            ("aliases", models.CharField(blank=True, help_text="Comma-separated search aliases", max_length=250)),
            ("mode", models.CharField(choices=[("factor", "Factor"), ("formula", "Formula (scale + offset)")], default="factor", max_length=12)),
            ("scale", models.DecimalField(decimal_places=20, default=Decimal("1"), help_text="base = value × scale + offset", max_digits=40)),
            ("offset", models.DecimalField(decimal_places=20, default=Decimal("0"), max_digits=40)),
            ("definition", models.TextField(blank=True)), ("order", models.PositiveSmallIntegerField(default=0)),
            ("is_active", models.BooleanField(default=True)),
            ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="units", to="converters.category")),
        ], options={"ordering": ("order", "name")}),
        migrations.CreateModel(name="FeaturedConversion", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("order", models.PositiveSmallIntegerField(default=0)),
            ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="converters.category")),
            ("from_unit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="featured_from", to="converters.unit")),
            ("to_unit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="featured_to", to="converters.unit")),
        ], options={"ordering": ("order",)}),
        migrations.AddConstraint(model_name="unit", constraint=models.UniqueConstraint(fields=("category", "slug"), name="unique_unit_slug_per_category")),
    ]
