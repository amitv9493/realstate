# Generated by Django 5.0.8 on 2024-11-10 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0026_stripetranscation_identifier_stripetranscation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripetranscation',
            name='amt',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]