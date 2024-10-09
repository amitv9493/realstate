# Generated by Django 5.0.8 on 2024-10-08 17:11

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_alter_paypalpayementhistory_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paypalpayementhistory',
            name='success',
        ),
        migrations.AddField(
            model_name='paypalpayementhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='paypalpayementhistory',
            name='transcation_type',
            field=models.CharField(choices=[('INITIATED', 'Initiated'), ('FAILED', 'Failed'), ('COMPLETED', 'Completed')], max_length=50),
        ),
    ]
