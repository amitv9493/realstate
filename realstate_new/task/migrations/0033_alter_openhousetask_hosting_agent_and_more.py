# Generated by Django 5.0.8 on 2024-09-26 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0032_openhousetask_hosting_agent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openhousetask',
            name='hosting_agent',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='openhousetask',
            name='listing_agent',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
