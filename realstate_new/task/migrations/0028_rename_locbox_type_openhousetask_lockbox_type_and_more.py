# Generated by Django 5.0.8 on 2024-09-24 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0027_lockboxtask_alarm_code_lockboxtask_concierge_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='openhousetask',
            old_name='locbox_type',
            new_name='lockbox_type',
        ),
        migrations.RenameField(
            model_name='professionalservicetask',
            old_name='locbox_type',
            new_name='lockbox_type',
        ),
        migrations.RenameField(
            model_name='runnertask',
            old_name='locbox_type',
            new_name='lockbox_type',
        ),
        migrations.RenameField(
            model_name='showingtask',
            old_name='locbox_type',
            new_name='lockbox_type',
        ),
        migrations.RemoveField(
            model_name='lockboxtask',
            name='locbox_type',
        ),
        migrations.RemoveField(
            model_name='signtask',
            name='locbox_type',
        ),
    ]
