# Generated by Django 5.0.8 on 2024-09-11 07:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0022_alter_lockbox_lockbox_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockbox',
            name='lockbox_task',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lockbox', to='task.lockboxtask', verbose_name='Lock Boxes'),
        ),
    ]
