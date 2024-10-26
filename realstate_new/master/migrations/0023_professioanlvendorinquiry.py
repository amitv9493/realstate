# Generated by Django 5.0.8 on 2024-10-26 07:37

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0022_lockbox_property_lockbox'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfessioanlVendorInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client_phone', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, null=True, size=None)),
                ('client_email', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, null=True, size=None)),
                ('preferred_name', models.CharField(default='', max_length=50)),
                ('preferred_method_of_contact', models.CharField(choices=[('PHONE', 'PHONE'), ('EMAIL', 'EMAIL')])),
                ('service_skill', models.CharField(choices=[('PHOTO', 'Photography')], default='PHOTO', max_length=50)),
                ('mile_radius_preference', models.CharField(default='', max_length=50, verbose_name='Area Covered')),
                ('additional_notes', models.TextField(default='')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
