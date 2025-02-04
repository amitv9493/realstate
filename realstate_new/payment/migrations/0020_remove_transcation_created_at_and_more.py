# Generated by Django 5.0.7 on 2024-11-01 18:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('payment', '0019_transcation_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transcation',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='transcation',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='transcation',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='transcation',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transcation',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transcation',
            name='status',
            field=models.CharField(choices=[('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('INITIATED', 'INITIATED')], default='INITIATED', max_length=50),
        ),
        migrations.AlterField(
            model_name='transcation',
            name='transcation_id',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddIndex(
            model_name='transcation',
            index=models.Index(fields=['content_type', 'object_id'], name='payment_tra_content_47c7ab_idx'),
        ),
    ]
