# Generated by Django 5.0.8 on 2024-09-27 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0013_remove_property_listing_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='city',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='property',
            name='state',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='property',
            name='street',
            field=models.CharField(max_length=255),
        ),
    ]
