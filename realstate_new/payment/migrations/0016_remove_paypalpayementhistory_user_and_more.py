# Generated by Django 5.0.8 on 2024-10-08 17:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0015_paypalpayementhistory_content_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paypalpayementhistory',
            name='user',
        ),
        migrations.AddField(
            model_name='paypalpayementhistory',
            name='payble_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payble', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paypalpayementhistory',
            name='payble_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiveble', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paypalpayementhistory',
            name='transcation_type',
            field=models.CharField(choices=[('INITIATED', 'Initiated'), ('FAILED', 'Failed'), ('COMPLETED', 'Completed'), ('RECEIVED', 'Received')], max_length=50),
        ),
    ]
