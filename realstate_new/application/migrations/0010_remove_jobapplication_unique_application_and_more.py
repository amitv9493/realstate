# Generated by Django 5.0.8 on 2024-10-27 05:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_alter_jobapplication_applicant'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='jobapplication',
            name='unique-application',
        ),
        migrations.RemoveIndex(
            model_name='jobapplication',
            name='application_content_9dbae3_idx',
        ),
        migrations.RenameField(
            model_name='jobapplication',
            old_name='task_id',
            new_name='object_id',
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='jobapplication',
            index=models.Index(fields=['content_type', 'object_id'], name='application_content_5166a2_idx'),
        ),
        migrations.AddConstraint(
            model_name='jobapplication',
            constraint=models.UniqueConstraint(fields=('object_id', 'content_type', 'applicant'), name='unique-application', violation_error_message='The record already exists.'),
        ),
    ]
