from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("converters", "0001_initial")]
    operations = [
        migrations.AddField(model_name="unit", name="source_name", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="unit", name="source_url", field=models.URLField(blank=True)),
        migrations.AddField(model_name="unit", name="verified_on", field=models.DateField(blank=True, null=True)),
        migrations.AlterField(model_name="unit", name="mode", field=models.CharField(choices=[("factor", "Factor"), ("formula", "Formula (scale + offset)"), ("reciprocal", "Reciprocal")], default="factor", max_length=12)),
        migrations.CreateModel(name="CurrencyRate", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("base", models.CharField(max_length=3)), ("quote", models.CharField(max_length=3)),
            ("rate", models.DecimalField(decimal_places=20, max_digits=40)),
            ("rate_date", models.DateField(blank=True, null=True)), ("fetched_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ("base", "quote")}),
        migrations.AddConstraint(model_name="currencyrate", constraint=models.UniqueConstraint(fields=("base", "quote"), name="unique_currency_pair")),
    ]
