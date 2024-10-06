# Generated by Django 5.0.8 on 2024-10-06 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_notification_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='event',
            field=models.CharField(choices=[('CREATED', 'Task Created'), ('ASSIGNED', 'Task Assigned'), ('STARTED', 'Task Started'), ('COMPLETED', 'Task Completed'), ('CREATER_CANCELLED', 'Task Cancelled by creater'), ('ASSIGNER_CANCELLED', 'Task Cancelled by assigner'), ('REASSIGNED', 'Task Reassigned'), ('DETAILS_UPDATED', 'Details Updated')], max_length=20),
        ),
    ]
