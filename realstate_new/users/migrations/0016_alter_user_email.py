# Generated by Django 5.0.8 on 2024-09-28 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_rename_office_name_user_brokerage_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]