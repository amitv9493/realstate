# Generated by Django 5.0.7 on 2024-11-01 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0082_lockboxtask_lockbox_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockboxtask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='openhousetask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='professionalservicetask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='runnertask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='showingtask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='signtask',
            name='payment_verified',
            field=models.BooleanField(default=True),
        ),
    ]
