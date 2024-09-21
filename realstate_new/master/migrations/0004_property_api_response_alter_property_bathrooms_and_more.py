# Generated by Django 5.0.7 on 2024-09-19 18:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_alter_property_lot_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='api_response',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='bathrooms',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='property',
            name='bedrooms',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='property',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='property',
            name='listing_date',
            field=models.DateField(default=datetime.datetime(2024, 9, 19, 18, 17, 58, 423359, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='property',
            name='lot_size',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='mls_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='property',
            name='price',
            field=models.PositiveIntegerField(default=0, verbose_name='Current Listing Price'),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_address',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(choices=[('SFH', 'Single Family Home'), ('CONDO', 'Condo'), ('APT', 'Apartment'), ('COMM', 'Commercial'), ('OTHER', 'Other')], default='OTHER', max_length=50),
        ),
        migrations.AlterField(
            model_name='property',
            name='square_footage',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='year_built',
            field=models.PositiveIntegerField(default=0),
        ),
    ]