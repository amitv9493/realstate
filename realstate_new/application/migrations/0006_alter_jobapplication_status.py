# Generated by Django 5.0.8 on 2024-09-27 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_remove_jobapplication_unique_application_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), ('CLAIMED', 'CLAIMED')], default='PENDING', max_length=20),
        ),
    ]
