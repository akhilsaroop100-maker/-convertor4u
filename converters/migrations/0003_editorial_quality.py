from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("converters", "0002_accuracy_and_currency_rates")]
    operations = [
        migrations.AddField(model_name="category", name="guide_intro", field=models.TextField(blank=True)),
        migrations.AddField(model_name="category", name="real_world_uses", field=models.TextField(blank=True)),
        migrations.AddField(model_name="category", name="rounding_guidance", field=models.TextField(blank=True)),
        migrations.AddField(model_name="category", name="regional_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="category", name="common_mistakes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="category", name="faq", field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name="category", name="reviewed_by", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="category", name="reviewed_on", field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name="featuredconversion", name="is_editorially_reviewed", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="featuredconversion", name="reviewed_by", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="featuredconversion", name="reviewed_on", field=models.DateField(blank=True, null=True)),
        migrations.AddConstraint(model_name="featuredconversion", constraint=models.UniqueConstraint(fields=("category", "from_unit", "to_unit"), name="unique_featured_conversion")),
        migrations.CreateModel(
            name="CorrectionReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("page_url", models.URLField(blank=True)),
                ("subject", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("resolved", models.BooleanField(default=False)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
