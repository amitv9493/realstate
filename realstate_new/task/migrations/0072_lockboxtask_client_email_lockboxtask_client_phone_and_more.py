# Generated by Django 5.0.8 on 2024-10-14 16:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0071_remove_lockboxtask_alarm_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockboxtask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='lockboxtask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='openhousetask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='openhousetask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='professionalservicetask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='professionalservicetask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='runnertask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='runnertask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='showingtask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='showingtask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='signtask',
            name='client_email',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='signtask',
            name='client_phone',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None),
        ),
    ]
