# Generated by Django 5.0.8 on 2024-09-27 08:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0013_remove_property_listing_date'),
        ('task', '0043_remove_runnertask_vebdor_notes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signtask',
            name='collection_address',
        ),
        migrations.AddField(
            model_name='signtask',
            name='install_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
        migrations.AddField(
            model_name='signtask',
            name='pickup_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
        migrations.AddField(
            model_name='signtask',
            name='remove_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
        migrations.AlterField(
            model_name='signtask',
            name='dropoff_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='master.property'),
        ),
    ]