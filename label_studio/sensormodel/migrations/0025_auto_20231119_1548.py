# Generated by Django 3.1.14 on 2023-11-19 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensormodel', '0024_sensor_manual_offset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='manual_offset',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
