# Generated by Django 5.0.7 on 2024-09-21 06:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_alter_property_api_response_alter_property_features_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='listing_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
