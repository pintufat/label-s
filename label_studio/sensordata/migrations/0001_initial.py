# Generated by Django 3.2.16 on 2023-05-10 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sensormodel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('project_id', models.IntegerField(blank=True, null=True)),
                ('begin_datetime', models.DateTimeField(blank=True, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('file_hash', models.CharField(blank=True, max_length=10, null=True)),
                ('sensortype', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sensormodel.sensortype')),
            ],
        ),
    ]
