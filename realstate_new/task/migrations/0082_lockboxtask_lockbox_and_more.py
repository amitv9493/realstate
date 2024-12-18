# Generated by Django 5.0.8 on 2024-10-26 04:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('master', '0022_lockbox_property_lockbox'),
        ('task', '0081_verificationdocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockboxtask',
            name='lockbox',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='master.lockbox'),
        ),
        migrations.AddIndex(
            model_name='verificationdocument',
            index=models.Index(fields=['content_type', 'object_id'], name='task_verifi_content_2b46ba_idx'),
        ),
    ]
