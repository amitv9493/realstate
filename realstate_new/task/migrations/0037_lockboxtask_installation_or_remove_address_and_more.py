# Generated by Django 5.0.8 on 2024-09-26 17:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0012_alter_property_lotsize_sqft'),
        ('task', '0036_remove_lockboxtask_installation_or_remove_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockboxtask',
            name='installation_or_remove_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
        migrations.AddField(
            model_name='lockboxtask',
            name='pickup_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
    ]
