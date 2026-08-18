from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("converters", "0003_editorial_quality")]
    operations = [
        migrations.AddField(model_name="featuredconversion", name="show_on_homepage", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="featuredconversion", name="homepage_order", field=models.PositiveSmallIntegerField(default=0)),
    ]
