# Generated by Django 5.0.8 on 2024-11-03 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0021_transcation_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcation',
            name='nonce',
            field=models.TextField(default=''),
        ),
    ]
