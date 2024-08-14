# Generated by Django 4.2.13 on 2024-08-13 19:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("data_manager", "0011_auto_20240718_1355"),
    ]

    operations = [
        migrations.AlterField(
            model_name="view",
            name="user",
            field=models.ForeignKey(
                help_text="User who made this view",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)ss",
                to=settings.AUTH_USER_MODEL,
            ),
        )
    ]
