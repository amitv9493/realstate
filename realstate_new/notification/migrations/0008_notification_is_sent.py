# Generated by Django 5.0.8 on 2024-11-20 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0007_alter_notification_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]