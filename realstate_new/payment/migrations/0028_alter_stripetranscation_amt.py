# Generated by Django 5.0.8 on 2024-11-20 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0027_alter_stripetranscation_amt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripetranscation',
            name='amt',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
