# Generated by Django 5.0.8 on 2024-11-08 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_user_stripe_customer_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='uuid',
        ),
    ]