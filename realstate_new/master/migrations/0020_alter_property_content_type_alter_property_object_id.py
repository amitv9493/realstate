# Generated by Django 5.0.8 on 2024-10-14 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('master', '0019_property_content_type_property_object_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='object_id',
            field=models.PositiveIntegerField(),
        ),
    ]
