# Generated by Django 5.0.7 on 2024-10-05 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0056_taskhistory_extra_data_alter_taskhistory_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskhistory',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
