# Generated by Django 5.0.8 on 2024-09-27 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0041_runnertask_dropoff_address_runnertask_pickup_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnertask',
            name='instructions',
            field=models.TextField(blank=True, default=''),
        ),
    ]