# Generated by Django 5.0.8 on 2024-10-06 06:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('event', models.CharField(choices=[('CREATED', 'Task Created'), ('ASSIGNED', 'Task Assigned'), ('STARTED', 'Task Started'), ('COMPLETED', 'Task Completed'), ('CREATER_CANCELLED', 'Task Cancelled by creater'), ('ASSIGNER_CANCELLED', 'Task Cancelled by assigner'), ('REASSIGNED', 'Task Reassigned')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, default='')),
                ('extra_data', models.JSONField(default=dict)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='notificatio_content_743343_idx')],
            },
        ),
    ]
