# Generated by Django 3.1.13 on 2021-09-07 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_export', '0003_auto_20210907_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='counters',
            field=models.JSONField(default=dict, verbose_name='Exporting meta data'),
        ),
    ]
