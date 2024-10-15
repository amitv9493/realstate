# Generated by Django 5.0.8 on 2024-10-14 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0021_delete_propertyfeature'),
        ('task', '0077_remove_runnertask_instructions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='runnertask',
            name='property_address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='master.property'),
        ),
    ]