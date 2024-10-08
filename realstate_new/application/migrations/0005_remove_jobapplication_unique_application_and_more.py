# Generated by Django 5.0.7 on 2024-08-07 07:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_jobapplication_unique_application'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='jobapplication',
            name='unique-application',
        ),
        migrations.AddConstraint(
            model_name='jobapplication',
            constraint=models.UniqueConstraint(fields=('object_id', 'content_type', 'applicant'), name='unique-application', violation_error_message='The record already exists.'),
        ),
    ]
