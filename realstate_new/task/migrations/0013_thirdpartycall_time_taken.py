# Generated by Django 5.0.6 on 2024-07-17 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0012_thirdpartycall'),
    ]

    operations = [
        migrations.AddField(
            model_name='thirdpartycall',
            name='time_taken',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
